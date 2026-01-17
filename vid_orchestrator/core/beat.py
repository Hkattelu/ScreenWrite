"""
Beat dataclass representing a logical segment of a video script.

A Beat is a 5-10 second segment containing script text, auto-calculated duration,
and metadata for B-roll asset fetching.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Beat:
    """
    Represents a single logical segment of a video script.
    
    A Beat contains the script text, auto-calculated duration based on word count,
    and search queries for fetching B-roll assets from various sources.
    
    Attributes:
        id: Unique identifier for the beat (e.g., "beat_001")
        text: The actual script text for this beat
        stock_keyword: Search term for stock footage (e.g., "person typing on keyboard")
        youtube_search_phrase: Search term for YouTube (e.g., "programmer coding tutorial")
        duration: Duration in seconds (auto-calculated from word count)
        asset_paths: Mapping of fetcher names to downloaded file paths
    """
    
    id: str
    text: str
    stock_keyword: str
    youtube_search_phrase: str
    duration: float = field(init=False)
    asset_paths: Dict[str, Optional[str]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Auto-calculate duration from word count using 2.5 words per second heuristic."""
        word_count = len(self.text.split())
        self.duration = word_count / 2.5
        self.validate()
    
    def validate(self):
        """
        Validate that the beat meets requirements.
        
        Raises:
            AssertionError: If duration is not in 5-10 second range or text is empty
        """
        # Check required fields first
        assert self.text.strip(), f"Beat {self.id}: Text cannot be empty"
        assert self.stock_keyword.strip(), f"Beat {self.id}: Stock keyword cannot be empty"
        assert self.youtube_search_phrase.strip(), f"Beat {self.id}: YouTube search phrase cannot be empty"
        
        # Then check duration bounds
        assert 5 <= self.duration <= 10, (
            f"Beat {self.id}: Duration {self.duration:.1f}s not in 5-10 second range. "
            f"Text has {len(self.text.split())} words."
        )
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the beat."""
        return (
            f"Beat(id='{self.id}', duration={self.duration:.1f}s, "
            f"words={len(self.text.split())}, text='{self.text[:50]}...')"
        )