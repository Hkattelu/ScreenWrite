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
from typing import Optional, List, Dict, Any
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
    def _search_with_retry(self, query: str, count: int = 1) -> Optional[List[str]]:
        """Search YouTube with retry logic."""
        return self._search(query, count=count)
    
    @retry_with_backoff(
        max_retries=2,
        base_delay=2.0,
        exceptions=(NetworkError, Exception)
    )
    def _download_with_retry(self, video_url: str, query: str, target_duration: float = None, progress_callback=None) -> Optional[str]:
        """Download video with retry logic."""
        return self._download(video_url, query, target_duration=target_duration, progress_callback=progress_callback)
    
    @retry_with_backoff(
        max_retries=1,
        base_delay=1.0,
        exceptions=(Exception,)
    )
    def _trim_video_with_retry(self, input_path: str, duration: float, start_time: float = 0) -> Optional[str]:
        """Trim video with retry logic."""
        return self._trim_video(input_path, duration, start_time)
    
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
        results = self.fetch_multi(query, duration, count=1)
        return results[0] if results else None
    
    def search(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Search for videos without downloading them.
        
        Args:
            query: Search query string
            count: Number of results to return
            
        Returns:
            List of video metadata dictionaries with id, title, thumbnail_url, duration
        """
        if not self._yt_dlp_available:
            logger.error("yt-dlp not available, cannot search YouTube")
            return []
            
        if not query.strip():
            logger.error("Empty query provided to YouTube search")
            return []
        
        try:
            # Search for videos
            entries = self._search_with_retry(query, count=count)
            if not entries:
                logger.warning(f"No YouTube results found for query: {query}")
                return []
            
            # Process entries into metadata format
            results = []
            for entry in entries:
                try:
                    # Extract relevant metadata directly from search result if available
                    video_id = entry.get('id', '')
                    if not video_id:
                        continue
                        
                    title = entry.get('title', 'Untitled')
                    duration = entry.get('duration', 0.0)
                    
                    # Get best thumbnail
                    thumbnails = entry.get('thumbnails', [])
                    thumbnail_url = ''
                    if thumbnails:
                        thumbnail_url = thumbnails[-1].get('url', '')
                    
                    video_url = entry.get('url') or f"https://www.youtube.com/watch?v={video_id}"
                    
                    # If we have basic info but duration is missing, we MIGHT want to fetch it,
                    # but for speed we'll accept what search gives us. 
                    # Most search results DO include duration.
                    results.append({
                        'id': video_id,
                        'title': title,
                        'thumbnail_url': thumbnail_url,
                        'duration': float(duration) if duration else 0.0,
                        'url': video_url
                    })
                except Exception as e:
                    logger.warning(f"Failed to process search entry: {e}")
                    continue
            
            return results
            
        except Exception as e:
            log_error_with_context(
                logger, logging.ERROR,
                "YouTube search failed",
                component="YouTubeClient",
                query=query,
                error=e
            )
            return []
    
    def _get_video_metadata(self, video_url: str) -> Optional[Dict[str, Any]]:
        """
        Get video metadata without downloading.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Dictionary with id, title, thumbnail_url, duration
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'socket_timeout': 30,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                if not info:
                    return None
                
                # Extract relevant metadata
                video_id = info.get('id', '')
                title = info.get('title', 'Untitled')
                duration = info.get('duration', 0)
                
                # Get best thumbnail
                thumbnails = info.get('thumbnails', [])
                thumbnail_url = ''
                if thumbnails:
                    # Prefer high quality thumbnails
                    thumbnail_url = thumbnails[-1].get('url', '')
                
                return {
                    'id': video_id,
                    'title': title,
                    'thumbnail_url': thumbnail_url,
                    'duration': float(duration) if duration else 0.0,
                    'url': video_url
                }
                
        except Exception as e:
            logger.warning(f"Failed to get metadata for {video_url}: {e}")
            return None
    
    def download_by_id(self, video_id: str, metadata: Dict[str, Any], target_duration: float = None, progress_callback=None) -> Optional[str]:
        """
        Download a specific video by ID using metadata from search.
        
        Args:
            video_id: YouTube video ID
            metadata: Metadata dictionary from search containing url
            target_duration: Optional target duration in seconds to optimize download
            progress_callback: Optional function(percent, status) to report progress
            
        Returns:
            Path to downloaded video file, or None if failed
        """
        if not self._yt_dlp_available:
            logger.error("yt-dlp not available, cannot download from YouTube")
            return None
        
        try:
            # Get video URL from metadata or construct it
            video_url = metadata.get('url', f"https://www.youtube.com/watch?v={video_id}")
            
            # Download using existing method
            downloaded_path = self._download_with_retry(
                video_url, 
                video_id, 
                target_duration=target_duration,
                progress_callback=progress_callback
            )
            
            return downloaded_path
            
        except Exception as e:
            logger.error(f"Failed to download YouTube video {video_id}: {e}")
            return None

    def download_segment(self, video_id: str, metadata: Dict[str, Any], start_time: float, duration: float, progress_callback=None) -> Optional[str]:
        """
        Download a specific segment of a video.
        
        Args:
            video_id: YouTube video ID
            metadata: Metadata dictionary
            start_time: Start time in seconds
            duration: Duration in seconds
            progress_callback: Optional progress callback
            
        Returns:
            Path to downloaded and trimmed segment
        """
        if not self._yt_dlp_available:
            return None
            
        try:
            video_url = metadata.get('url', f"https://www.youtube.com/watch?v={video_id}")
            
            # We want to optimize download by only pulling the part we need
            # but yt-dlp's download_sections can be flaky with offsets.
            # For "Simple B-Roll", accuracy is key.
            # We'll download the chunk starting at start_time and ending at start_time + duration + cushion
            
            cushion = 10 # 10s cushion for safety
            
            # Download using smart pulling if possible
            downloaded_path = self._download_with_retry(
                video_url,
                f"{video_id}_segment_{start_time}",
                target_duration=start_time + duration + cushion,
                progress_callback=progress_callback
            )
            
            if not downloaded_path:
                return None
                
            # Now trim to EXACT segment
            trimmed_path = self._trim_video_with_retry(downloaded_path, duration, start_time)
            
            # Cleanup source
            if trimmed_path and trimmed_path != downloaded_path:
                try:
                    os.remove(downloaded_path)
                except:
                    pass
                return trimmed_path
            
            return downloaded_path
            
        except Exception as e:
            logger.error(f"Failed to download segment for {video_id}: {e}")
            return None

    def fetch_multi(self, query: str, duration: float, count: int = 3) -> List[str]:
        """
        Fetch multiple videos from YouTube matching the query and trim them.
        
        Args:
            query: Search query string
            duration: Target duration in seconds
            count: Number of candidates to fetch
            
        Returns:
            List of paths to downloaded and trimmed video files
        """
        if not self._yt_dlp_available:
            logger.error("yt-dlp not available, cannot fetch from YouTube")
            return []
            
        if not query.strip():
            logger.error("Empty query provided to YouTube fetcher")
            return []
            
        try:
            # Search for videos with retry logic
            video_urls = self._search_with_retry(query, count=count)
            if not video_urls:
                logger.warning(f"No YouTube results found for query: {query}")
                return []
            
            downloaded_paths = []
            for i, video_url in enumerate(video_urls):
                try:
                    # Download video with retry logic
                    downloaded_path = self._download_with_retry(video_url, f"{query}_{i}")
                    if not downloaded_path:
                        continue
                    
                    # Trim video to target duration if ffmpeg is available
                    if self._ffmpeg_available:
                        trimmed_path = self._trim_video_with_retry(downloaded_path, duration)
                        if trimmed_path:
                            try:
                                os.remove(downloaded_path)
                            except OSError:
                                pass
                            downloaded_paths.append(trimmed_path)
                        else:
                            downloaded_paths.append(downloaded_path)
                    else:
                        downloaded_paths.append(downloaded_path)
                except Exception as e:
                    logger.warning(f"Failed to fetch candidate {i} from YouTube: {e}")
                    continue
            
            return downloaded_paths
                
        except Exception as e:
            log_error_with_context(
                logger, logging.ERROR,
                "Unexpected error fetching multiple from YouTube",
                component="YouTubeClient",
                query=query,
                error=e
            )
            return []


    def _search(self, query: str, count: int = 1) -> Optional[List[Dict[str, Any]]]:
        """
        Search YouTube for videos matching the query.
        
        Args:
            query: Search query string
            count: Number of results to return
            
        Returns:
            List of dictionaries containing matching video info, or None if no results
            
        Raises:
            NetworkError: If network-related errors occur
        """
        try:
            # Configure yt-dlp for search
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # Don't download, just get metadata
                'default_search': f'ytsearch{count}:',
                'socket_timeout': 20,  # Increased timeout for initial search
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search for videos
                search_results = ydl.extract_info(f"ytsearch{count}:{query}", download=False)
                
                if not search_results or 'entries' not in search_results:
                    return None
                    
                entries = search_results['entries']
                if not entries or len(entries) == 0:
                    return None
                
                return list(entries[:count])
                    
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

    def _download(self, video_url: str, query: str, target_duration: float = None, progress_callback=None) -> Optional[str]:
        """
        Download video from YouTube URL.
        
        Args:
            video_url: YouTube video URL
            query: Original search query (for filename)
            target_duration: Optional target duration in seconds to optimize download
            progress_callback: Optional function(percent, status) to report progress
            
        Returns:
            Path to downloaded video file, or None if failed
            
        Raises:
            NetworkError: If download fails
        """
        # Handle dict input if passed by mistake
        if isinstance(video_url, dict):
            video_url = video_url.get('url')
            
        if not video_url:
            return None
            
        try:
            # Generate safe filename from query
            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_query = safe_query.replace(' ', '_')[:50]  # Limit length
            
            output_template = str(self.output_dir / f"youtube_{safe_query}_%(id)s.%(ext)s")
            
            # Progress hook for yt-dlp
            def yt_dlp_hook(d):
                if progress_callback:
                    if d['status'] == 'downloading':
                        try:
                            # Extract percentage
                            p = d.get('_percent_str', '0%').replace('%', '').strip()
                            percent = float(p)
                            progress_callback(percent, 'downloading')
                        except:
                            pass
                    elif d['status'] == 'finished':
                        progress_callback(100, 'processing')

            # Determine format based on ffmpeg availability
            if self._ffmpeg_available:
                # Use a broader format selector if ffmpeg is available
                # Prioritize single file formats for better compatibility
                format_selector = 'best[ext=mp4][height<=1080]/best[height<=1080]/bestvideo[height<=1080]+bestaudio/best'
            else:
                # Select best format that has both video and audio (pre-merged)
                format_selector = 'best[ext=mp4]/best'

            base_opts = {
                'format': format_selector,
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'socket_timeout': 60,
                'retries': 3,
                'cachedir': False,
                'nocheckcertificate': True,
                'progress_hooks': [yt_dlp_hook] if progress_callback else [],
            }

            # Smart Pulling: Limit download to a section if target_duration is provided
            if target_duration and self._ffmpeg_available:
                # Limit download to first part of video (30s minimum or 2x duration)
                # This prevents pulling hour-long videos for a 5s beat.
                limit = max(30, target_duration * 2)
                base_opts['download_sections'] = [
                    {'start_time': 0, 'end_time': limit}
                ]
                base_opts['force_keyframes_at_cuts'] = True

            # Common browser headers
            browser_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
            }

            # Strategies to try in order of likelihood to succeed
            strategies = [
                # Try Android Creator client (often bypasses main 403 blocks)
                {'extractor_args': {'youtube': {'player_client': ['android_creator']}}},
                
                # Try Web Embedded client (often lenient)
                {'extractor_args': {'youtube': {'player_client': ['web_embedded']}}, 'http_headers': browser_headers},
                
                # Try Android client proper
                {'extractor_args': {'youtube': {'player_client': ['android']}}},
                
                # Try iOS client (might work for some videos)
                {'extractor_args': {'youtube': {'player_client': ['ios']}}},
                
                # Try using browser cookies (as fallback if clients fail)
                {'cookiesfrombrowser': ('chrome',), 'http_headers': browser_headers},
                {'cookiesfrombrowser': ('edge',), 'http_headers': browser_headers},
                {'cookiesfrombrowser': ('firefox',), 'http_headers': browser_headers},
                
                # Default fallback
                {'http_headers': browser_headers}
            ]
            
            last_error = None
            
            for strategy in strategies:
                try:
                    current_opts = base_opts.copy()
                    current_opts.update(strategy)
                    
                    # Log strategy being attempted (debug only)
                    strategy_name = list(strategy.keys())[0] if strategy else "default"
                    logger.debug(f"Attempting download with strategy: {strategy_name}")

                    with yt_dlp.YoutubeDL(current_opts) as ydl:
                        # Download the video
                        info = ydl.extract_info(video_url, download=True)
                        
                        if not info:
                            continue
                        
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
                        
                        # If we got here, download "succeeded" but file missing? 
                        # This might happen if it was merged to mkv but we looked for mp4
                        # We should have found it above.
                        
                except Exception as e:
                    # Capture specific errors
                    error_msg = str(e).lower()
                    
                    # CRITICAL: If the user cancelled, we MUST re-raise immediately
                    # otherwise the loop will just try the next strategy.
                    if "cancelled" in error_msg:
                        raise
                        
                    if "browser" in error_msg and "cookie" in error_msg:
                        logger.debug(f"Strategy {strategy} failed (likely browser not found/locked): {e}")
                    elif "403" in error_msg or "forbidden" in error_msg:
                        logger.warning(f"Strategy {strategy} failed with 403 Forbidden: {e}")
                    else:
                        logger.warning(f"Strategy {strategy} failed: {e}")
                    
                    last_error = e
                    continue
            
            # If all strategies failed
            if last_error:
                raise last_error
            return None
                    
        except Exception as e:
            # If "empty file" error occurs with ffmpeg available (handled partially above, but catching global fails here)
            if "empty" in str(e).lower() and self._ffmpeg_available:
                 # One last desperate try with simple format and no complex opts
                 try:
                    logger.warning("All strategies failed. Trying fallback 'best' format...")
                    fallback_opts = {
                        'format': 'best',
                        'outtmpl': output_template,
                         'quiet': True,
                    }
                    with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                        info = ydl.extract_info(video_url, download=True)
                        filename = ydl.prepare_filename(info)
                        if os.path.exists(filename):
                             return filename
                 except Exception:
                     pass

            log_error_with_context(
                logger, logging.ERROR,
                "YouTube download failed",
                component="YouTubeClient",
                video_url=video_url,
                query=query,
                error=e
            )
            # Re-raise as NetworkError for consistent handling
            raise NetworkError(f"YouTube download failed: {e}")
    
    def _trim_video(self, input_path: str, duration: float, start_time: float = 0) -> Optional[str]:
        """
        Trim video to target duration using ffmpeg.
        
        Args:
            input_path: Path to input video file
            duration: Target duration in seconds
            start_time: Start time in seconds
            
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
            # Using -ss before -i for fast seeking
            cmd = [
                'ffmpeg',
                '-ss', str(start_time),  # Start time
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
