"""Asset fetching components for downloading B-roll from various sources."""

from .base_fetcher import AssetFetcher
from .youtube_client import YouTubeClient
from .pexels_client import PexelsClient
from .asset_orchestrator import AssetOrchestrator

__all__ = ['AssetFetcher', 'YouTubeClient', 'PexelsClient', 'AssetOrchestrator']