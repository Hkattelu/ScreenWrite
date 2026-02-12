"""
Abstract base class for asset fetchers.

Defines the interface that all asset fetchers must implement for downloading
B-roll ScreenWrite from various sources.
"""

from abc import ABC, abstractmethod
from typing import Optional, List


class AssetFetcher(ABC):
    """
    Abstract base class for fetching video assets from external sources.
    
    All asset fetchers must implement the fetch method to download videos
    matching a search query and target duration.
    """
    
    @abstractmethod
    def fetch(self, query: str, duration: float) -> Optional[str]:
        """
        Fetch a video asset matching the given query and duration.
        
        Args:
            query: Search query string (e.g., "person typing on keyboard")
            duration: Target duration in seconds for the video
            
        Returns:
            Path to the downloaded video file, or None if fetching failed
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass

    def fetch_multi(self, query: str, duration: float, count: int = 3) -> List[str]:
        """
        Fetch multiple candidate video assets matching the given query and duration.
        
        Args:
            query: Search query string
            duration: Target duration in seconds
            count: Number of candidates to fetch
            
        Returns:
            List of paths to downloaded video files. May be fewer than count if failed.
        """
        # Default implementation just calls fetch once
        result = self.fetch(query, duration)
        return [result] if result else []
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the name of this fetcher for logging and identification.
        
        Returns:
            Human-readable name of the fetcher (e.g., "YouTube", "Pexels")
        """
        pass

    @abstractmethod
    def search(self, query: str, count: int = 5) -> List[dict]:
        """
        Search for assets without downloading them.
        
        Args:
            query: Search query string
            count: Number of results to return
            
        Returns:
            List of asset metadata dictionaries
        """
        pass

    @abstractmethod
    def download_by_id(self, asset_id: str, metadata: dict, progress_callback=None) -> Optional[str]:
        """
        Download a specific asset by its ID and metadata.
        
        Args:
            asset_id: Unique identifier for the asset
            metadata: Metadata returned by the search method
            progress_callback: Optional function(percent, status) to report progress
            
        Returns:
            Path to the downloaded file, or None if failed
        """
        pass
