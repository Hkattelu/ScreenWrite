"""
Abstract base class for asset fetchers.

Defines the interface that all asset fetchers must implement for downloading
B-roll ScreenWrite from various sources.
"""

from abc import ABC, abstractmethod
from typing import Optional


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
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the name of this fetcher for logging and identification.
        
        Returns:
            Human-readable name of the fetcher (e.g., "YouTube", "Pexels")
        """
        pass
