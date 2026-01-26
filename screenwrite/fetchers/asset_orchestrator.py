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
        Fetch an asset using the fallback strategy with caching support.
        
        Tries YouTube first with youtube_query, then falls back to Pexels
        with stock_query if YouTube fails. Returns the path to the first
        successfully downloaded asset.
        
        Args:
            youtube_query: Search query for YouTube
            stock_query: Search query for stock ScreenWrite (Pexels)
            duration: Target duration in seconds
            beat_id: Optional beat identifier for logging context
            enable_cache: Whether to use the persistent asset cache (default: True)
            
        Returns:
            Path to downloaded video file, or None if all fetchers failed
        """
        beat_context = f"[{beat_id}] " if beat_id else ""
        
        if not self.fetchers:
            logger.error(f"{beat_context}No asset fetchers available")
            return None
        
        if not youtube_query.strip() and not stock_query.strip():
            logger.error(f"{beat_context}Both YouTube and stock queries are empty")
            return None
        
        # Track which fetchers we've tried for logging
        attempted_fetchers = []
        
        for fetcher in self.fetchers:
            try:
                # Choose appropriate query based on fetcher type
                if isinstance(fetcher, YouTubeClient):
                    query = youtube_query
                    if not query.strip():
                        logger.debug(f"{beat_context}Skipping {fetcher.name} - empty YouTube query")
                        continue
                elif isinstance(fetcher, PexelsClient):
                    query = stock_query
                    if not query.strip():
                        logger.debug(f"{beat_context}Skipping {fetcher.name} - empty stock query")
                        continue
                else:
                    # For any other fetcher types, try YouTube query first, then stock
                    query = youtube_query if youtube_query.strip() else stock_query
                    if not query.strip():
                        logger.debug(f"{beat_context}Skipping {fetcher.name} - no valid query")
                        continue
                
                # Check cache first
                if enable_cache:
                    cached_path = find_in_asset_cache(query, duration, fetcher.name)
                    if cached_path:
                        # Copy from cache to output directory
                        try:
                            cached_file = Path(cached_path)
                            output_ext = cached_file.suffix
                            safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
                            safe_query = safe_query.replace(' ', '_')[:30]
                            
                            target_filename = f"cached_{fetcher.name.lower()}_{safe_query}_{cached_file.name}{output_ext}"
                            target_path = Path(self.output_dir) / target_filename
                            
                            shutil.copy2(cached_path, target_path)
                            logger.info(f"{beat_context}Cache hit for {fetcher.name}: '{query}' -> {target_path}")
                            return str(target_path)
                        except Exception as e:
                            logger.warning(f"{beat_context}Failed to copy from cache: {e}")

                logger.info(f"{beat_context}Attempting to fetch asset using {fetcher.name} with query: '{query}'")
                attempted_fetchers.append(fetcher.name)
                
                # Try to fetch the asset
                asset_path = fetcher.fetch(query, duration)
                
                if asset_path:
                    # Verify the file actually exists and is not empty
                    try:
                        file_path = Path(asset_path)
                        if file_path.exists() and file_path.stat().st_size > 0:
                            logger.info(f"{beat_context}Successfully fetched asset using {fetcher.name}: {asset_path}")
                            
                            # Save to cache if enabled
                            if enable_cache:
                                saved_cache = save_to_asset_cache(asset_path, query, duration, fetcher.name)
                                if saved_cache:
                                    logger.debug(f"{beat_context}Saved asset to cache: {saved_cache}")
                                    
                            return asset_path
                        else:
                            logger.warning(f"{beat_context}{fetcher.name} returned invalid file path: {asset_path}")
                    except Exception as e:
                        logger.warning(f"{beat_context}Error verifying file from {fetcher.name}: {e}")
                else:
                    logger.info(f"{beat_context}{fetcher.name} failed to fetch asset for query: '{query}'")
                    
            except Exception as e:
                logger.error(f"{beat_context}Unexpected error with {fetcher.name} fetcher: {e}")
                attempted_fetchers.append(f"{fetcher.name} (error)")
                continue
        
        # All fetchers failed
        if attempted_fetchers:
            logger.warning(f"{beat_context}All asset fetchers failed. Tried: {', '.join(attempted_fetchers)}")
        else:
            logger.warning(f"{beat_context}No suitable fetchers available for the given queries")
        
        return None
    
    def fetch_assets_batch(self, 
                          queries: List[Dict[str, Any]],
                          max_workers: int = 4,
                          enable_cache: bool = True) -> Dict[str, Optional[str]]:
        """
        Fetch multiple assets in batch using parallel threads with caching.
        
        Args:
            queries: List of query dictionaries, each containing:
                - 'id': Unique identifier for the query
                - 'youtube_query': YouTube search query
                - 'stock_query': Stock ScreenWrite search query  
                - 'duration': Target duration in seconds
            max_workers: Maximum number of parallel download threads (default: 4)
            enable_cache: Whether to use the persistent asset cache (default: True)
                
        Returns:
            Dictionary mapping query IDs to downloaded file paths (or None if failed)
        """
        results = {}
        
        if not queries:
            logger.warning("No queries provided for batch fetching")
            return results
        
        logger.info(f"Starting parallel batch fetch for {len(queries)} assets (max_workers={max_workers}, cache={enable_cache})")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Map futures to their query IDs
            future_to_id = {}
            for i, q in enumerate(queries, 1):
                query_id = q.get('id', f'query_{i}')
                yt_query = q.get('youtube_query', '')
                st_query = q.get('stock_query', '')
                duration = q.get('duration', 5.0)
                
                future = executor.submit(
                    self.fetch_asset, 
                    yt_query, 
                    st_query, 
                    duration, 
                    beat_id=query_id,
                    enable_cache=enable_cache
                )
                future_to_id[future] = query_id

            # Process completed downloads
            iterator = as_completed(future_to_id)
            if HAS_RICH:
                iterator = track(iterator, total=len(queries), description="Fetching assets...", disable=not HAS_RICH)
            
            for future in iterator:
                query_id = future_to_id[future]
                try:
                    asset_path = future.result()
                    results[query_id] = asset_path
                    
                    if asset_path:
                        logger.debug(f"Parallel fetch for {query_id} succeeded: {asset_path}")
                    else:
                        logger.debug(f"Parallel fetch for {query_id} failed")
                except Exception as e:
                    logger.error(f"Error in parallel fetch thread for {query_id}: {e}")
                    results[query_id] = None
        
        # Log batch summary
        successful = sum(1 for path in results.values() if path is not None)
        total = len(results)
        logger.info(f"Parallel batch fetch completed: {successful}/{total} assets downloaded successfully")
        
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
            
            # Add fetcher-specific status information
            if isinstance(fetcher, YouTubeClient):
                fetcher_status.update({
                    'yt_dlp_available': getattr(fetcher, '_yt_dlp_available', False),
                    'ffmpeg_available': getattr(fetcher, '_ffmpeg_available', False)
                })
            elif isinstance(fetcher, PexelsClient):
                fetcher_status.update({
                    'api_available': getattr(fetcher, '_api_available', False),
                    'has_api_key': bool(getattr(fetcher, 'api_key', None))
                })
            
            status[fetcher.name] = fetcher_status
        
        return status

