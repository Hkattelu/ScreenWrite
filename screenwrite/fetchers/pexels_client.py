"""
Pexels asset fetcher using Pexels API for downloading stock B-roll ScreenWrite.

This module provides the PexelsClient class that searches Pexels for videos
matching a query and downloads the first result. It handles API key management,
rate limiting, and various error conditions gracefully.
"""

import os
import requests
import tempfile
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from urllib.parse import urlparse

from .base_fetcher import AssetFetcher
from ..utils.error_handling import (
    retry_with_backoff,
    validate_api_key,
    NetworkError,
    handle_graceful_degradation,
    log_error_with_context
)


logger = logging.getLogger(__name__)


class PexelsClient(AssetFetcher):
    """
    Pexels asset fetcher using Pexels API for stock video download.
    
    This class searches Pexels for videos matching a query and downloads the first
    result. It handles API key management, rate limiting, and network failures
    gracefully.
    """
    
    def __init__(self, api_key: Optional[str] = None, output_dir: str = None):
        """
        Initialize the Pexels client.
        
        Args:
            api_key: Pexels API key. If None, will try to get from environment variable.
            output_dir: Directory to save downloaded videos. If None, uses temp directory.
        """
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir())
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv('PEXELS_API_KEY')
        
        # Validate API key if provided
        if self.api_key:
            validation_result = validate_api_key(self.api_key, 'Pexels')
            if not validation_result.is_valid:
                logger.error(f"Invalid Pexels API key: {validation_result.error_message}")
                self._api_available = False
                self.api_key = None
            else:
                self._api_available = True
                # Log any warnings about the API key
                for warning in validation_result.warnings:
                    logger.warning(f"Pexels API key warning: {warning}")
                logger.debug("Pexels API key validated successfully")
        else:
            logger.warning("No Pexels API key provided. Pexels fetching will be unavailable.")
            self._api_available = False
            
        # Pexels API configuration
        self.base_url = "https://api.pexels.com/videos"
        self.headers = {
            'Authorization': self.api_key,
            'User-Agent': 'screenwrite/1.0'
        } if self.api_key else {}
        
        # Session for connection pooling with timeout configuration
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Configure session timeouts and retries
        adapter = requests.adapters.HTTPAdapter(
            max_retries=requests.adapters.Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504]
            )
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    @property
    def name(self) -> str:
        """Return the name of this fetcher."""
        return "Pexels"
    
    def fetch(self, query: str, duration: float) -> Optional[str]:
        """
        Fetch a video from Pexels matching the query.
        
        Args:
            query: Search query string (stock keyword)
            duration: Target duration in seconds (not used for Pexels search)
            
        Returns:
            Path to the downloaded video file, or None if failed
        """
        results = self.fetch_multi(query, duration, count=1)
        return results[0] if results else None

    def fetch_multi(self, query: str, duration: float, count: int = 3) -> List[str]:
        """
        Fetch multiple videos from Pexels matching the query.
        
        Args:
            query: Search query string
            duration: Target duration in seconds
            count: Number of candidates to fetch
            
        Returns:
            List of paths to downloaded video files
        """
        if not self._api_available:
            logger.error("Pexels API key not available, cannot fetch from Pexels")
            return []
            
        if not query.strip():
            logger.error("Empty query provided to Pexels fetcher")
            return []
            
        try:
            # Search for videos with retry logic
            videos_info = self._search_with_retry(query, count=count)
            if not videos_info:
                logger.warning(f"No Pexels results found for query: {query}")
                return []
            
            downloaded_paths = []
            for i, video_info in enumerate(videos_info):
                # Download video with retry logic
                # We use a unique suffix for candidates
                downloaded_path = self._download_with_retry(video_info, f"{query}_{i}")
                if downloaded_path:
                    downloaded_paths.append(downloaded_path)
            
            return downloaded_paths
                
        except Exception as e:
            log_error_with_context(
                logger, logging.ERROR,
                "Unexpected error fetching multiple from Pexels",
                component="PexelsClient",
                query=query,
                error=e
            )
            return []
    
    @retry_with_backoff(
        max_retries=2,
        base_delay=1.0,
        exceptions=(NetworkError, requests.exceptions.RequestException)
    )
    def _search_with_retry(self, query: str, count: int = 1) -> Optional[List[Dict[str, Any]]]:
        """Search Pexels with retry logic."""
        return self._search(query, count=count)
    
    @retry_with_backoff(
        max_retries=2,
        base_delay=2.0,
        exceptions=(NetworkError, requests.exceptions.RequestException)
    )
    def _download_with_retry(self, video_info: Dict[str, Any], query: str) -> Optional[str]:
        """Download video with retry logic."""
        return self._download(video_info, query)
    
    def _search(self, query: str, count: int = 1) -> Optional[List[Dict[str, Any]]]:
        """
        Search Pexels for videos matching the query.
        
        Args:
            query: Search query string
            count: Number of results to return
            
        Returns:
            List of video information dicts, or None if no results
            
        Raises:
            NetworkError: If network-related errors occur
        """
        try:
            # Build search URL
            search_url = f"{self.base_url}/search"
            params = {
                'query': query,
                'per_page': count,
                'orientation': 'landscape',  # Prefer landscape videos
                'size': 'medium'  # Medium quality for reasonable file size
            }
            
            # Make API request with timeout
            response = self.session.get(
                search_url, 
                params=params, 
                timeout=(10, 30)  # (connect_timeout, read_timeout)
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                logger.warning("Pexels API rate limit exceeded")
                raise NetworkError("Pexels API rate limit exceeded")
            
            # Handle authentication errors
            if response.status_code == 401:
                logger.error("Pexels API authentication failed - check API key")
                raise NetworkError("Pexels API authentication failed")
            
            # Handle other HTTP errors
            if response.status_code != 200:
                error_msg = f"Pexels API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg += f" - {error_data['error']}"
                except:
                    error_msg += f" - {response.text[:200]}"
                
                logger.error(error_msg)
                raise NetworkError(error_msg)
            
            # Parse response
            try:
                data = response.json()
            except ValueError as e:
                raise NetworkError(f"Invalid JSON response from Pexels API: {e}")
            
            if not data.get('videos') or len(data['videos']) == 0:
                logger.info(f"No Pexels videos found for query: {query}")
                return None
            
            results = []
            for video in data['videos'][:count]:
                # Extract video files (different quality options)
                video_files = video.get('video_files', [])
                if not video_files:
                    continue
                
                # Find best quality video file (prefer HD, fallback to SD)
                best_file = None
                for file_info in video_files:
                    quality = file_info.get('quality', '').lower()
                    file_type = file_info.get('file_type', '').lower()
                    
                    # Prefer mp4 format
                    if file_type == 'video/mp4':
                        if quality in ['hd', 'sd'] and (best_file is None or quality == 'hd'):
                            best_file = file_info
                
                # Fallback to any available file
                if not best_file and video_files:
                    best_file = video_files[0]
                
                if best_file and 'link' in best_file:
                    results.append({
                        'id': video.get('id'),
                        'url': best_file['link'],
                        'width': best_file.get('width'),
                        'height': best_file.get('height'),
                        'quality': best_file.get('quality'),
                        'file_type': best_file.get('file_type')
                    })
            
            return results if results else None
                    
        except requests.exceptions.Timeout:
            raise NetworkError(f"Pexels API timeout for query: {query}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Pexels API connection error: {e}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Pexels API request failed: {e}")
        except Exception as e:
            log_error_with_context(
                logger, logging.ERROR,
                "Pexels search failed",
                component="PexelsClient",
                query=query,
                error=e
            )
            raise NetworkError(f"Pexels search error: {e}")
    
    def _download(self, video_info: Dict[str, Any], query: str) -> Optional[str]:
        """
        Download video from Pexels URL.
        
        Args:
            video_info: Video information dict from search
            query: Original search query (for filename)
            
        Returns:
            Path to downloaded video file, or None if failed
            
        Raises:
            NetworkError: If network-related errors occur
        """
        try:
            video_url = video_info['url']
            video_id = video_info.get('id', 'unknown')
            
            # Generate safe filename from query
            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_query = safe_query.replace(' ', '_')[:50]  # Limit length
            
            # Determine file extension from URL or content type
            parsed_url = urlparse(video_url)
            url_ext = os.path.splitext(parsed_url.path)[1]
            if not url_ext:
                url_ext = '.mp4'  # Default to mp4
            
            output_filename = f"pexels_{safe_query}_{video_id}{url_ext}"
            output_path = self.output_dir / output_filename
            
            # Download the video with streaming and progress
            logger.debug(f"Downloading Pexels video from: {video_url}")
            
            response = self.session.get(
                video_url, 
                stream=True, 
                timeout=(10, 120)  # (connect_timeout, read_timeout)
            )
            response.raise_for_status()
            
            # Check content length for reasonable file size
            content_length = response.headers.get('content-length')
            if content_length:
                file_size_mb = int(content_length) / (1024 * 1024)
                if file_size_mb > 500:  # 500MB limit
                    logger.warning(f"Pexels video is very large ({file_size_mb:.1f}MB)")
                elif file_size_mb < 0.1:  # Less than 100KB
                    logger.warning(f"Pexels video is very small ({file_size_mb:.1f}MB)")
            
            # Write file in chunks with progress tracking
            total_size = 0
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            # Verify file was downloaded successfully
            if output_path.exists() and output_path.stat().st_size > 0:
                file_size_mb = output_path.stat().st_size / (1024 * 1024)
                logger.debug(f"Successfully downloaded Pexels video: {output_path} ({file_size_mb:.1f}MB)")
                return str(output_path)
            else:
                logger.error("Downloaded file is empty or missing")
                # Clean up empty file
                try:
                    if output_path.exists():
                        output_path.unlink()
                except OSError:
                    pass
                return None
                    
        except requests.exceptions.Timeout:
            raise NetworkError(f"Pexels download timeout for video: {video_info.get('id')}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Pexels download connection error: {e}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Pexels download request failed: {e}")
        except Exception as e:
            log_error_with_context(
                logger, logging.ERROR,
                "Pexels download failed",
                component="PexelsClient",
                video_id=video_info.get('id'),
                query=query,
                error=e
            )
            raise NetworkError(f"Pexels download error: {e}")
    
    def __del__(self):
        """Clean up session on destruction."""
        if hasattr(self, 'session'):
            self.session.close()
