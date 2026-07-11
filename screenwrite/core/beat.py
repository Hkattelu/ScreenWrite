"""
Beat dataclass representing a logical segment of a video script.

A Beat is a 5-10 second segment containing script text, auto-calculated duration,
and metadata for B-roll asset fetching.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..config import WORDS_PER_SECOND, BEAT_TEXT_TRUNCATION_LENGTH

__all__ = ['Beat']


@dataclass
class Beat:
    """
    Represents a single logical segment of a video script.
    
    A Beat contains the script text, auto-calculated duration based on word count,
    and search queries for fetching B-roll assets from various sources.
    
    Attributes:
        id: Unique identifier for the beat (e.g., "beat_001")
        text: The actual script text for this beat
        stock_keyword: Search term for stock ScreenWrite (e.g., "person typing on keyboard")
        youtube_search_phrase: Search term for YouTube (e.g., "programmer coding tutorial")
        duration: Duration in seconds (auto-calculated from word count)
        asset_paths: Mapping of fetcher names to downloaded file paths
        game: Resolved game title for the script (e.g. "Dark Souls"), or None
            when the script is not in game mode
        entities: Named in-game entities this beat is about (e.g. ["Bell
            Gargoyles"]), extracted by the LLM entity step
        beat_class: Routing class - "game_entity" | "abstract" | "manual_fill"
            | "unclassified" (legacy pipeline)
        candidates: Fetched candidate clips for this beat, as
            AssetCandidate.to_dict() dicts extended with the chosen segment
            window and the downloaded 'local_path'
    """

    id: str
    text: str
    stock_keyword: str
    youtube_search_phrase: str
    duration: float = field(init=False)
    asset_paths: Dict[str, Optional[str]] = field(default_factory=dict)
    visual_type: str = 'auto'
    visual_content: Optional[str] = None
    game: Optional[str] = None
    entities: List[str] = field(default_factory=list)
    beat_class: str = 'unclassified'
    candidates: List[dict] = field(default_factory=list)
    
    def __post_init__(self):
        """Auto-calculate duration from word count using the configured words per second heuristic."""
        word_count = len(self.text.split())
        self.duration = word_count / WORDS_PER_SECOND
        self.validate()
    
    def validate(self):
        """
        Validate that the beat meets requirements.
        
        Raises:
            AssertionError: If duration is invalid or text is empty
        """
        # Check required fields first
        assert self.text.strip(), f"Beat {self.id}: Text cannot be empty"
        # Note: Keywords can be empty if no B-roll is desired for this beat
        
        # Allow beats 3-10 seconds (more lenient for edge cases)
        # Minimum 3s for short transitions, maximum 10s for content
        assert 3 <= self.duration <= 10, (
            f"Beat {self.id}: Duration {self.duration:.1f}s not in 3-10 second range. "
            f"Text has {len(self.text.split())} words."
        )
    
    def __str__(self) -> str:
        """Return a human-readable string representation of the beat.
        
        Returns:
            Readable string representation of the Beat object
        """
        return f"[{self.id}] {self.duration:.1f}s: {self.text[:BEAT_TEXT_TRUNCATION_LENGTH]}..."
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the beat.
        
        Returns:
            Formatted string representation of the Beat object
        """
        return (
            f"Beat(id='{self.id}', duration={self.duration:.1f}s, "
            f"words={len(self.text.split())}, text='{self.text[:BEAT_TEXT_TRUNCATION_LENGTH]}...', "
            f"type='{self.visual_type}')"
        )
