"""Asset fetching components for downloading B-roll from various sources."""

from .base_fetcher import AssetFetcher
from .youtube_client import YouTubeClient
from .pexels_client import PexelsClient
from .chaptered_gameplay_fetcher import ChapteredGameplayFetcher
from .wiki_still_fetcher import WikiStillFetcher
from .asset_orchestrator import AssetOrchestrator

__all__ = [
    'AssetFetcher', 'YouTubeClient', 'PexelsClient',
    'ChapteredGameplayFetcher', 'WikiStillFetcher', 'AssetOrchestrator',
]