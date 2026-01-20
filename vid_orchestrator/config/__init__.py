"""Configuration and constants for vid-orchestrator."""

from .constants import (
    # Beat generation constants
    TARGET_MIN_DURATION,
    TARGET_MAX_DURATION,
    WORDS_PER_SECOND,
    
    # Encoding constants
    SUPPORTED_ENCODINGS,
    
    # File validation constants
    MIN_FILE_SIZE,
    MAX_FILE_SIZE,
    VALID_MARKDOWN_EXTENSIONS,
    
    # API validation constants
    MIN_API_KEY_LENGTH,
    MAX_API_KEY_LENGTH,
    
    # Disk space warning threshold
    LOW_DISK_SPACE_THRESHOLD,
    
    # Video generation constants
    DEFAULT_FRAMERATE,
    DEFAULT_VIDEO_WIDTH,
    DEFAULT_VIDEO_HEIGHT,
    
    # Timeout constants
    NETWORK_TIMEOUT,
    SUBPROCESS_TIMEOUT,
    
    # FCPXML generation constants
    MIN_FCPXML_FILE_SIZE,
    
    # Text truncation for logs
    BEAT_TEXT_TRUNCATION_LENGTH,
)

__all__ = [
    'TARGET_MIN_DURATION',
    'TARGET_MAX_DURATION',
    'WORDS_PER_SECOND',
    'SUPPORTED_ENCODINGS',
    'MIN_FILE_SIZE',
    'MAX_FILE_SIZE',
    'VALID_MARKDOWN_EXTENSIONS',
    'MIN_API_KEY_LENGTH',
    'MAX_API_KEY_LENGTH',
    'LOW_DISK_SPACE_THRESHOLD',
    'DEFAULT_FRAMERATE',
    'DEFAULT_VIDEO_WIDTH',
    'DEFAULT_VIDEO_HEIGHT',
    'NETWORK_TIMEOUT',
    'SUBPROCESS_TIMEOUT',
    'MIN_FCPXML_FILE_SIZE',
    'BEAT_TEXT_TRUNCATION_LENGTH',
]
