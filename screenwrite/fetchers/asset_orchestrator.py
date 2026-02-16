"""
Asset fetcher orchestrator with fallback logic.

This module provides the AssetOrchestrator class that coordinates multiple
asset fetchers with fallback logic. It tries YouTube first, then falls back
to Pexels if YouTube fails, and handles all error conditions gracefully.
"""

import logging
import shutil
from typing import List, Optional, Dict, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict

from .base_fetcher import AssetFetcher
from .youtube_client import YouTubeClient
from .pexels_client import PexelsClient
from ..utils.cache import find_in_asset_cache, save_to_asset_cache

try:
    from rich.progress import track
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


logger = logging.getLogger(__name__)


@dataclass
class AssetCandidate:
    """
    Represents a potential asset found during search that can be downloaded.
    
    Attributes:
        id: Unique identifier for this candidate (video_id for YouTube, id for Pexels)
        title: Human-readable title of the asset
        thumbnail_url: URL to thumbnail image for preview
        duration: Duration of the asset in seconds
        source: Source provider ("youtube" or "pexels")
        metadata: Source-specific metadata needed for download
    """
    id: str
    title: str
    thumbnail_url: str
    duration: float
    source: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class AssetOrchestrator:
    """
    Orchestrates multiple asset fetchers with fallback logic.
    
    This class manages a list of asset fetchers and tries them in order until
    one succeeds or all fail. It implements the YouTube â†’ Pexels fallback
    strategy and provides comprehensive error handling.
    """
    
    def __init__(self, 
                 pexels_api_key: Optional[str] = None,
                 output_dir: Optional[str] = None,
                 youtube_enabled: bool = True,
                 pexels_enabled: bool = True):
        """
        Initialize the asset orchestrator.
        
        Args:
            pexels_api_key: API key for Pexels. If None, will try environment variable.
            output_dir: Directory to save downloaded videos. If None, uses temp directory.
            youtube_enabled: Whether to enable YouTube fetching
            pexels_enabled: Whether to enable Pexels fetching
        """
        self.output_dir = output_dir
        self.fetchers: List[AssetFetcher] = []
        
        # Initialize fetchers in priority order (YouTube first, then Pexels)
        if youtube_enabled:
            try:
                youtube_client = YouTubeClient(output_dir=output_dir)
                self.fetchers.append(youtube_client)
                logger.info("YouTube fetcher initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize YouTube fetcher: {e}")
        
        if pexels_enabled:
            try:
                pexels_client = PexelsClient(api_key=pexels_api_key, output_dir=output_dir)
                self.fetchers.append(pexels_client)
                logger.info("Pexels fetcher initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Pexels fetcher: {e}")
        
        if not self.fetchers:
            logger.error("No asset fetchers available - all fetchers failed to initialize")
        else:
            fetcher_names = [f.name for f in self.fetchers]
            logger.info(f"Asset orchestrator initialized with fetchers: {', '.join(fetcher_names)}")
    
    def fetch_asset(self, 
                   youtube_query: str, 
                   stock_query: str, 
                   duration: float,
                   beat_id: str = None,
                   enable_cache: bool = True) -> Optional[str]:
        """
        Fetch a single asset using the fallback strategy.
        """
        results = self.fetch_assets(youtube_query, stock_query, duration, count=1, beat_id=beat_id, enable_cache=enable_cache)
        return results[0] if results else None
    
    def search_assets(self,
                     youtube_query: str,
                     stock_query: str,
                     duration: float,
                     count: int = 5) -> List[AssetCandidate]:
        """
        Search for asset candidates without downloading.
        
        Args:
            youtube_query: Search query for YouTube
            stock_query: Search query for stock footage (Pexels)
            duration: Target duration in seconds
            count: Number of candidates to return
            
        Returns:
            List of AssetCandidate objects with metadata
        """
        if not self.fetchers:
            logger.error("No asset fetchers available")
            return []
        
        if not youtube_query.strip() and not stock_query.strip():
            logger.error("Both YouTube and stock queries are empty")
            return []
        
        candidates = []
        
        for fetcher in self.fetchers:
            try:
                # Choose appropriate query based on fetcher name (duck typing)
                fetcher_name = getattr(fetcher, 'name', '').lower()
                if 'youtube' in fetcher_name:
                    query = youtube_query
                    if not query.strip():
                        continue
                elif 'pexels' in fetcher_name or 'stock' in fetcher_name:
                    query = stock_query
                    if not query.strip():
                        continue
                else:
                    query = youtube_query if youtube_query.strip() else stock_query
                    if not query.strip():
                        continue
                
                logger.info(f"Searching {fetcher.name} for: '{query}'")
                
                # Search without downloading
                search_results = fetcher.search(query, count=count - len(candidates))
                
                # Convert to AssetCandidate objects
                for result in search_results:
                    candidate = AssetCandidate(
                        id=result.get('id', ''),
                        title=result.get('title', 'Untitled'),
                        thumbnail_url=result.get('thumbnail_url', ''),
                        duration=result.get('duration', 0.0),
                        source=fetcher.name.lower(),
                        metadata=result
                    )
                    candidates.append(candidate)
                
                # If we have enough candidates, stop
                if len(candidates) >= count:
                    break
                    
            except Exception as e:
                logger.error(f"Unexpected error searching with {fetcher.name}: {e}")
                continue
        
        return candidates[:count]
    
    def download_candidate(self,
                          candidate: AssetCandidate,
                          beat_id: str = None,
                          target_duration: float = None,
                          progress_callback=None) -> Optional[str]:
        """
        Download a specific asset candidate.
        
        Args:
            candidate: AssetCandidate object with metadata
            beat_id: Optional beat identifier for logging context
            target_duration: Optional target duration in seconds to optimize download
            progress_callback: Optional function(percent, status) to report progress
            
        Returns:
            Path to downloaded file, or None if download failed
        """
        beat_context = f"[{beat_id}] " if beat_id else ""
        
        if not self.fetchers:
            logger.error(f"{beat_context}No asset fetchers available")
            return None
        
        # Find the appropriate fetcher based on source
        fetcher = None
        for f in self.fetchers:
            fetcher_name = getattr(f, 'name', '').lower()
            if candidate.source.lower() in fetcher_name:
                fetcher = f
                break
        
        if not fetcher:
            logger.error(f"{beat_context}No fetcher available for source: {candidate.source}")
            return None
        
        try:
            logger.info(f"{beat_context}Downloading candidate {candidate.id} from {candidate.source} (Target: {target_duration}s)")
            
            # Download the specific asset using metadata
            file_path = fetcher.download_by_id(
                candidate.id,
                candidate.metadata,
                target_duration=target_duration,
                progress_callback=progress_callback
            )
            
            if file_path and Path(file_path).exists():
                logger.info(f"{beat_context}Successfully downloaded to: {file_path}")
                return file_path
            else:
                logger.error(f"{beat_context}Download failed or file not found")
                return None
                
        except Exception as e:
            logger.error(f"{beat_context}Error downloading candidate {candidate.id}: {e}")
            return None

    def download_segment(self,
                        candidate: AssetCandidate,
                        start_time: float,
                        duration: float,
                        beat_id: str = None,
                        progress_callback=None) -> Optional[str]:
        """
        Download a specific segment of an asset candidate.
        """
        beat_context = f"[{beat_id}] " if beat_id else ""
        
        if not self.fetchers:
            logger.error(f"{beat_context}No asset fetchers available")
            return None
        
        # Find the appropriate fetcher based on source
        fetcher = None
        for f in self.fetchers:
            fetcher_name = getattr(f, 'name', '').lower()
            if candidate.source.lower() in fetcher_name:
                fetcher = f
                break
        
        if not fetcher:
            logger.error(f"{beat_context}No fetcher available for source: {candidate.source}")
            return None
        
        try:
            logger.info(f"{beat_context}Downloading segment of candidate {candidate.id} from {candidate.source} (Start: {start_time}s, Duration: {duration}s)")
            
            # Check if fetcher supports download_segment
            if hasattr(fetcher, 'download_segment'):
                file_path = fetcher.download_segment(
                    candidate.id,
                    candidate.metadata,
                    start_time=start_time,
                    duration=duration,
                    progress_callback=progress_callback
                )
            else:
                # Fallback: download whole (or optimized) then trim
                # This is already handled inside YouTubeClient.download_segment, 
                # but for other fetchers we might need fallback logic here.
                # For now, we only support segment download for YouTube.
                file_path = fetcher.download_by_id(
                    candidate.id,
                    candidate.metadata,
                    target_duration=start_time + duration,
                    progress_callback=progress_callback
                )
            
            if file_path and Path(file_path).exists():
                logger.info(f"{beat_context}Successfully downloaded segment to: {file_path}")
                return file_path
            else:
                logger.error(f"{beat_context}Segment download failed or file not found")
                return None
                
        except Exception as e:
            logger.error(f"{beat_context}Error downloading segment for {candidate.id}: {e}")
            return None

    def fetch_assets(self, 
                    youtube_query: str, 
                    stock_query: str, 
                    duration: float,
                    count: int = 3,
                    beat_id: str = None,
                    enable_cache: bool = True) -> List[str]:
        """
        Fetch multiple candidate assets using the fallback strategy.
        
        Args:
            youtube_query: Search query for YouTube
            stock_query: Search query for stock ScreenWrite (Pexels)
            duration: Target duration in seconds
            count: Number of candidates to fetch
            beat_id: Optional beat identifier for logging context
            enable_cache: Whether to use the persistent asset cache (default: True)
            
        Returns:
            List of paths to downloaded video files.
        """
        beat_context = f"[{beat_id}] " if beat_id else ""
        
        if not self.fetchers:
            logger.error(f"{beat_context}No asset fetchers available")
            return []
        
        if not youtube_query.strip() and not stock_query.strip():
            logger.error(f"{beat_context}Both YouTube and stock queries are empty")
            return []
        
        results = []
        attempted_fetchers = []
        
        for fetcher in self.fetchers:
            try:
                # Choose appropriate query based on fetcher name (duck typing)
                fetcher_name = getattr(fetcher, 'name', '').lower()
                if 'youtube' in fetcher_name:
                    query = youtube_query
                    if not query.strip():
                        continue
                elif 'pexels' in fetcher_name or 'stock' in fetcher_name:
                    query = stock_query
                    if not query.strip():
                        continue
                else:
                    query = youtube_query if youtube_query.strip() else stock_query
                    if not query.strip():
                        continue
                
                logger.info(f"{beat_context}Attempting to fetch {count} candidates using {fetcher.name} for: '{query}'")
                attempted_fetchers.append(fetcher.name)
                
                # Fetch multiple assets
                # Note: Cache handling for multi-assets is skipped for now for simplicity, 
                # but could be added similarly to fetch_asset
                fetcher_results = fetcher.fetch_multi(query, duration, count=count - len(results))
                
                for asset_path in fetcher_results:
                    if asset_path and Path(asset_path).exists():
                        results.append(asset_path)
                        
                # If we have enough results, stop
                if len(results) >= count:
                    break
                    
            except Exception as e:
                logger.error(f"{beat_context}Unexpected error with {fetcher.name} fetcher: {e}")
                continue
        
        return results[:count]
    
    def fetch_assets_batch(self, 
                          queries: List[Dict[str, Any]],
                          max_workers: int = 4,
                          enable_cache: bool = True,
                          candidates_per_beat: int = 3) -> Dict[str, List[str]]:
        """
        Fetch multiple assets in batch using parallel threads.
        
        Returns:
            Dictionary mapping query IDs to lists of downloaded file paths.
        """
        results = {}
        
        if not queries:
            logger.warning("No queries provided for batch fetching")
            return results
        
        logger.info(f"Starting parallel batch fetch for {len(queries)} assets (candidates={candidates_per_beat})")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {}
            for i, q in enumerate(queries, 1):
                query_id = q.get('id', f'query_{i}')
                yt_query = q.get('youtube_query', '')
                st_query = q.get('stock_query', '')
                duration = q.get('duration', 5.0)
                
                future = executor.submit(
                    self.fetch_assets, 
                    yt_query, 
                    st_query, 
                    duration, 
                    count=candidates_per_beat,
                    beat_id=query_id,
                    enable_cache=enable_cache
                )
                future_to_id[future] = query_id

            iterator = as_completed(future_to_id)
            if HAS_RICH:
                iterator = track(iterator, total=len(queries), description="Fetching assets...", disable=not HAS_RICH)
            
            for future in iterator:
                query_id = future_to_id[future]
                try:
                    asset_paths = future.result()
                    results[query_id] = asset_paths
                except Exception as e:
                    logger.error(f"Error in parallel fetch thread for {query_id}: {e}")
                    results[query_id] = []
        
        return results

    
    def get_available_fetchers(self) -> List[str]:
        """
        Get list of available fetcher names.
        
        Returns:
            List of fetcher names that are available and initialized
        """
        return [fetcher.name for fetcher in self.fetchers]
    
    def is_fetcher_available(self, fetcher_name: str) -> bool:
        """
        Check if a specific fetcher is available.
        
        Args:
            fetcher_name: Name of the fetcher to check
            
        Returns:
            True if the fetcher is available, False otherwise
        """
        return fetcher_name in self.get_available_fetchers()
    
    def get_fetcher_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed status information for all fetchers.
        
        Returns:
            Dictionary with fetcher names as keys and status info as values
        """
        status = {}
        
        for fetcher in self.fetchers:
            fetcher_status = {
                'name': fetcher.name,
                'available': True,
                'type': type(fetcher).__name__
            }
            
            # Add fetcher-specific status information based on name (duck typing)
            fetcher_name = getattr(fetcher, 'name', '').lower()
            if 'youtube' in fetcher_name:
                fetcher_status.update({
                    'yt_dlp_available': getattr(fetcher, '_yt_dlp_available', False),
                    'ffmpeg_available': getattr(fetcher, '_ffmpeg_available', False)
                })
            elif 'pexels' in fetcher_name or 'stock' in fetcher_name:
                fetcher_status.update({
                    'api_available': getattr(fetcher, '_api_available', False),
                    'has_api_key': bool(getattr(fetcher, 'api_key', None))
                })
            
            status[fetcher.name] = fetcher_status
        
        return status

