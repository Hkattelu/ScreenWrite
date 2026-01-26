"""
Constants and magic numbers for screenwrite.

This module centralizes all configuration values and magic numbers used throughout
the application, making them easy to adjust and maintain.
"""

# ============================================================================
# Beat Generation Constants
# ============================================================================

# Minimum and maximum beat duration in seconds
TARGET_MIN_DURATION = 5.0
TARGET_MAX_DURATION = 10.0

# Words per second heuristic for calculating beat duration
# Based on typical speaking rate of 2.5 words per second
WORDS_PER_SECOND = 2.5


def _validate_beat_constants():
    """Validate beat generation constants at import time."""
    errors = []
    
    if TARGET_MIN_DURATION <= 0:
        errors.append("TARGET_MIN_DURATION must be positive")
    if TARGET_MAX_DURATION <= 0:
        errors.append("TARGET_MAX_DURATION must be positive")
    if TARGET_MIN_DURATION >= TARGET_MAX_DURATION:
        errors.append(f"TARGET_MIN_DURATION ({TARGET_MIN_DURATION}) must be less than TARGET_MAX_DURATION ({TARGET_MAX_DURATION})")
    if WORDS_PER_SECOND <= 0:
        errors.append("WORDS_PER_SECOND must be positive")
    
    if errors:
        raise ValueError("Configuration validation errors in beat constants:\n  " + "\n  ".join(errors))


_validate_beat_constants()

# ============================================================================
# File Encoding Constants
# ============================================================================

# Supported encodings for markdown scripts, tried in order
SUPPORTED_ENCODINGS = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

# ============================================================================
# File Validation Constants
# ============================================================================

# Minimum file size in bytes (0 bytes is empty, which is invalid)
MIN_FILE_SIZE = 0

# Maximum file size in bytes (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Valid markdown file extensions
VALID_MARKDOWN_EXTENSIONS = ['.md', '.markdown', '.txt']


def _validate_file_constants():
    """Validate file handling constants at import time."""
    errors = []
    
    if MIN_FILE_SIZE < 0:
        errors.append("MIN_FILE_SIZE must be non-negative")
    if MAX_FILE_SIZE <= 0:
        errors.append("MAX_FILE_SIZE must be positive")
    if MIN_FILE_SIZE >= MAX_FILE_SIZE:
        errors.append(f"MIN_FILE_SIZE ({MIN_FILE_SIZE}) must be less than MAX_FILE_SIZE ({MAX_FILE_SIZE})")
    if not VALID_MARKDOWN_EXTENSIONS:
        errors.append("VALID_MARKDOWN_EXTENSIONS cannot be empty")
    
    if errors:
        raise ValueError("Configuration validation errors in file constants:\n  " + "\n  ".join(errors))


_validate_file_constants()

# ============================================================================
# API Key Validation Constants
# ============================================================================

# API key length bounds
MIN_API_KEY_LENGTH = 10
MAX_API_KEY_LENGTH = 200


def _validate_api_constants():
    """Validate API key constants at import time."""
    errors = []
    
    if MIN_API_KEY_LENGTH <= 0:
        errors.append("MIN_API_KEY_LENGTH must be positive")
    if MAX_API_KEY_LENGTH <= 0:
        errors.append("MAX_API_KEY_LENGTH must be positive")
    if MIN_API_KEY_LENGTH > MAX_API_KEY_LENGTH:
        errors.append(f"MIN_API_KEY_LENGTH ({MIN_API_KEY_LENGTH}) cannot exceed MAX_API_KEY_LENGTH ({MAX_API_KEY_LENGTH})")
    
    if errors:
        raise ValueError("Configuration validation errors in API constants:\n  " + "\n  ".join(errors))


_validate_api_constants()

# ============================================================================
# Disk Space Constants
# ============================================================================

# Warn if available disk space drops below this threshold (100 MB)
LOW_DISK_SPACE_THRESHOLD = 100 * 1024 * 1024

# ============================================================================
# Video Generation Constants
# ============================================================================

# Default framerate for generated timelines (frames per second)
DEFAULT_FRAMERATE = 30

# Default video resolution for FCPXML timelines
DEFAULT_VIDEO_WIDTH = 1920
DEFAULT_VIDEO_HEIGHT = 1080

# ============================================================================
# Timeout Constants
# ============================================================================

# Network timeout for HTTP requests (seconds)
NETWORK_TIMEOUT = 10.0

# Subprocess timeout for external commands like ffmpeg (seconds)
SUBPROCESS_TIMEOUT = 120

# ============================================================================
# FCPXML Generation Constants
# ============================================================================

# Minimum valid FCPXML file size in bytes (must have proper XML structure)
MIN_FCPXML_FILE_SIZE = 100

# ============================================================================
# Text Processing Constants
# ============================================================================

# Length to truncate beat text in logs and string representations
BEAT_TEXT_TRUNCATION_LENGTH = 50

