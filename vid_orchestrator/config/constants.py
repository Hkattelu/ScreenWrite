"""
Constants and magic numbers for vid-orchestrator.

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

# ============================================================================
# API Key Validation Constants
# ============================================================================

# API key length bounds
MIN_API_KEY_LENGTH = 10
MAX_API_KEY_LENGTH = 200

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
