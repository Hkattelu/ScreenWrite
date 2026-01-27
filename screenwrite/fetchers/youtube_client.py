"""
YouTube asset fetcher using yt-dlp for downloading B-roll ScreenWrite.

This module provides the YouTubeClient class that searches YouTube for videos
matching a query, downloads the first result, and trims it to the target duration
using ffmpeg.
"""

import os
import subprocess
import tempfile
import logging
from typing import Optional
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

from .base_fetcher import AssetFetcher
from ..utils.error_handling import (
    retry_with_backoff,
    check_dependency,
    NetworkError,
    DependencyError,
    handle_graceful_degradation,
    log_error_with_context
)


logger = logging.getLogger(__name__)


class YouTubeClient(AssetFetcher):
    """
    YouTube asset fetcher using yt-dlp for video download and ffmpeg for trimming.
    
    This class searches YouTube for videos matching a query, downloads the first
    result, and trims it to match the target duration. It handles various error
    conditions gracefully, including missing dependencies and network failures.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the YouTube client.
        
        Args:
            output_dir: Directory to save downloaded videos. If None, uses temp directory.
        """
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir())
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if yt-dlp is available
        if yt_dlp is None:
            logger.warning("yt-dlp not installed. YouTube fetching will be unavailable.")
            self._yt_dlp_available = False
        else:
            self._yt_dlp_available = True
            logger.debug("yt-dlp is available for YouTube fetching")
            
        # Check if ffmpeg is available using internal robust check
        self._ffmpeg_available = self._check_ffmpeg()
        
        if not self._ffmpeg_available:
            logger.warning("FFmpeg not available (check failed). Video trimming will be unavailable.")
        else:
            logger.debug("FFmpeg is available for video trimming")
    
    @property
    def name(self) -> str:
        """Return the name of this fetcher."""
        return "YouTube"
    
    @retry_with_backoff(
        max_retries=2,
        base_delay=1.0,
        exceptions=(NetworkError, Exception)
    )
    def _search_with_retry(self, query: str) -> Optional[str]:
        """Search YouTube with retry logic."""
        return self._search(query)
    
    @retry_with_backoff(
        max_retries=2,
        base_delay=2.0,
        exceptions=(NetworkError, Exception)
    )
    def _download_with_retry(self, video_url: str, query: str) -> Optional[str]:
        """Download video with retry logic."""
        return self._download(video_url, query)
    
    @retry_with_backoff(
        max_retries=1,
        base_delay=1.0,
        exceptions=(Exception,)
    )
    def _trim_video_with_retry(self, input_path: str, duration: float) -> Optional[str]:
        """Trim video with retry logic."""
        return self._trim_video(input_path, duration)
    
    def _check_ffmpeg(self) -> bool:
        """
        Check if ffmpeg is available on the system.
        
        Returns:
            True if ffmpeg is available, False otherwise
        """
        try:
            # On Windows, subprocess.run can return weird codes even if successful
            # Use 'where' on Windows or 'which' on Unix to check existence first
            import shutil
            if shutil.which("ffmpeg"):
                # Try running version command to be sure
                subprocess.run(
                    ["ffmpeg", "-version"], 
                    capture_output=True, 
                    check=False, # Don't raise on non-zero return code
                    timeout=10
                )
                # If we get here without exception, binary exists and is executable
                return True
            return False
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("ffmpeg check failed. Video trimming/merging will be unavailable.")
            return False
    
    def fetch(self, query: str, duration: float) -> Optional[str]:
        """
        Fetch a video from YouTube matching the query and trim to target duration.
        
        Args:
            query: Search query string
            duration: Target duration in seconds
            
        Returns:
            Path to the downloaded and trimmed video file, or None if failed
        """
        if not self._yt_dlp_available:
            logger.error("yt-dlp not available, cannot fetch from YouTube")
            return None
            
        if not query.strip():
            logger.error("Empty query provided to YouTube fetcher")
            return None
            
        try:
            # Search for video with retry logic
            video_url = self._search_with_retry(query)
            if not video_url:
                logger.warning(f"No YouTube results found for query: {query}")
                return None
            
            # Download video with retry logic
            downloaded_path = self._download_with_retry(video_url, query)
            if not downloaded_path:
                logger.error(f"Failed to download video from: {video_url}")
                return None
            
            # Trim video to target duration if ffmpeg is available
            if self._ffmpeg_available:
                trimmed_path = self._trim_video_with_retry(downloaded_path, duration)
                if trimmed_path:
                    # Remove original file to save space
                    try:
                        os.remove(downloaded_path)
                        logger.debug(f"Removed original file after trimming: {downloaded_path}")
                    except OSError as e:
                        logger.warning(f"Could not remove original file: {e}")
                    return trimmed_path
                else:
                    logger.warning("Video trimming failed, returning original file")
                    return downloaded_path
            else:
                logger.info("ffmpeg unavailable, returning untrimmed video")
                return downloaded_path
                
        except Exception as e:
            log_error_with_context(
                logger, logging.ERROR,
                "Unexpected error fetching from YouTube",
                component="YouTubeClient",
                query=query,
                duration=duration,
                error=e
            )
            return None

    def _search(self, query: str) -> Optional[str]:
        """
        Search YouTube for videos matching the query.
        
        Args:
            query: Search query string
            
        Returns:
            URL of the first matching video, or None if no results
            
        Raises:
            NetworkError: If network-related errors occur
        """
        try:
            # Configure yt-dlp for search
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Don't download, just get metadata
                'default_search': 'ytsearch1:',  # Search YouTube, return 1 result
                'socket_timeout': 30,  # 30 second timeout
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search for videos
                search_results = ydl.extract_info(f"ytsearch1:{query}", download=False)
                
                if not search_results or 'entries' not in search_results:
                    return None
                    
                entries = search_results['entries']
                if not entries or len(entries) == 0:
                    return None
                
                # Return URL of first result
                first_result = entries[0]
                if 'url' in first_result:
                    return first_result['url']
                elif 'id' in first_result:
                    return f"https://www.youtube.com/watch?v={first_result['id']}"
                else:
                    return None
                    
        except yt_dlp.utils.DownloadError as e:
            # Network or YouTube-specific errors
            raise NetworkError(f"YouTube search failed: {e}")
        except Exception as e:
            log_error_with_context(
                logger, logging.ERROR,
                "YouTube search failed",
                component="YouTubeClient",
                query=query,
                error=e
            )
            raise NetworkError(f"YouTube search error: {e}")

    def _download(self, video_url: str, query: str) -> Optional[str]:
        """
        Download video from YouTube URL.
        
        Args:
            video_url: YouTube video URL
            query: Original search query (for filename)
            
        Returns:
            Path to downloaded video file, or None if failed
            
        Raises:
            NetworkError: If network-related errors occur
        """
        try:
            # Generate safe filename from query
            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_query = safe_query.replace(' ', '_')[:50]  # Limit length
            
            output_template = str(self.output_dir / f"youtube_{safe_query}_%(id)s.%(ext)s")
            
            # Determine format based on ffmpeg availability
            # If ffmpeg is missing, we must avoid formats that need merging (video+audio)
            if self._ffmpeg_available:
                # Use a broader format selector if ffmpeg is available
                # best[height<=720] might fail if no 720p is available, fallback to best
                format_selector = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best'
            else:
                # Select best format that has both video and audio (pre-merged)
                format_selector = 'best[ext=mp4]/best'

            # Configure yt-dlp for download
            ydl_opts = {
                'format': format_selector,
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 60,  # 60 second timeout
                'retries': 3,  # Built-in yt-dlp retries
                # Force ffmpeg location if available in path but check failed weirdly
                # 'ffmpeg_location': 'ffmpeg' 
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Download the video
                info = ydl.extract_info(video_url, download=True)
                
                if not info:
                    return None
                
                # Find the downloaded file
                filename = ydl.prepare_filename(info)
                if os.path.exists(filename):
                    logger.debug(f"Successfully downloaded: {filename}")
                    return filename
                else:
                    # Sometimes the extension changes, try to find the file
                    base_name = os.path.splitext(filename)[0]
                    for ext in ['.mp4', '.webm', '.mkv', '.avi']:
                        candidate = base_name + ext
                        if os.path.exists(candidate):
                            logger.debug(f"Found downloaded file with different extension: {candidate}")
                            return candidate
                    return None
                    
        except yt_dlp.utils.DownloadError as e:
            # If "empty file" error occurs, it might be an ffmpeg merge failure
            # Try falling back to a pre-merged format even if we thought we had ffmpeg
            if "empty" in str(e).lower() and self._ffmpeg_available:
                logger.warning("Download failed with empty file, trying fallback format without merge...")
                try:
                    ydl_opts['format'] = 'best[ext=mp4]/best'
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(video_url, download=True)
                        filename = ydl.prepare_filename(info)
                        if os.path.exists(filename):
                             return filename
                except Exception as retry_e:
                    logger.error(f"Fallback download also failed: {retry_e}")
            
            # Network or YouTube-specific errors
            raise NetworkError(f"YouTube download failed: {e}")
        except Exception as e:
            log_error_with_context(
                logger, logging.ERROR,
                "YouTube download failed",
                component="YouTubeClient",
                video_url=video_url,
                query=query,
                error=e
            )
            raise NetworkError(f"YouTube download error: {e}")
    
    def _trim_video(self, input_path: str, duration: float) -> Optional[str]:
        """
        Trim video to target duration using ffmpeg.
        
        Args:
            input_path: Path to input video file
            duration: Target duration in seconds
            
        Returns:
            Path to trimmed video file, or None if failed
        """
        if not self._ffmpeg_available:
            logger.warning("ffmpeg not available, cannot trim video")
            return None
            
        try:
            # Generate output filename
            input_file = Path(input_path)
            output_path = input_file.parent / f"trimmed_{input_file.name}"
            
            # Build ffmpeg command
            cmd = [
                'ffmpeg',
                '-i', str(input_path),
                '-t', str(duration),  # Duration
                '-c', 'copy',  # Copy streams without re-encoding for speed
                '-avoid_negative_ts', 'make_zero',  # Handle timestamp issues
                '-y',  # Overwrite output file
                str(output_path)
            ]
            
            # Run ffmpeg with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                # Verify output file has reasonable size
                output_size = os.path.getsize(output_path)
                if output_size > 0:
                    logger.debug(f"Successfully trimmed video to {duration}s: {output_path}")
                    return str(output_path)
                else:
                    logger.error("Trimmed video file is empty")
                    # Clean up empty file
                    try:
                        os.remove(output_path)
                    except OSError:
                        pass
                    return None
            else:
                log_error_with_context(
                    logger, logging.ERROR,
                    "ffmpeg failed",
                    component="YouTubeClient",
                    return_code=result.returncode,
                    stderr=result.stderr[:500] if result.stderr else "No error output"
                )
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"ffmpeg timeout while trimming video: {input_path}")
            return None
        except Exception as e:
            log_error_with_context(
                logger, logging.ERROR,
                "Video trimming failed",
                component="YouTubeClient",
                input_path=input_path,
                duration=duration,
                error=e
            )
            return None
