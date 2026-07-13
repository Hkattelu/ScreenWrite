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


# ============================================================================
# Keyword Generation Constants
# ============================================================================

# Stop words for generating stock keywords
STOCK_KEYWORD_STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'your', 'first', 'then', 'now', 'here', 'there', 'when', 'where', 'how'
}

# Visual patterns for generating stock keywords
# Keys are the strong search terms we want to use
# Values are the trigger words found in text that map to these terms
VISUAL_PATTERNS = {
    'coding': ['coding', 'programming', 'developer', 'programmer', 'code', 'script'],
    'computer': ['computer', 'laptop', 'keyboard', 'screen', 'monitor', 'desktop'],
    'typing': ['typing', 'type', 'input', 'enter'],
    'studying': ['tutorial', 'learning', 'education', 'student', 'study', 'reading'],
    'office': ['office', 'meeting', 'presentation', 'team', 'work', 'business', 'colleague'],
    'writing': ['writing', 'editor', 'file', 'document', 'text', 'paper', 'note'],
    'technology': ['terminal', 'command', 'console', 'shell', 'data', 'database', 'server', 'system'],
    'person': ['person', 'people', 'man', 'woman', 'user'],
    'digital': ['software', 'application', 'program', 'digital', 'tech', 'app']
}

# Stop words for generating YouTube search phrases
YOUTUBE_PHRASE_STOP_WORDS = {
    'this', 'that', 'with', 'from', 'they', 'have', 'will', 'been',
    'were', 'said', 'each', 'which', 'their', 'time', 'would', 'then',
    'first', 'need', 'your', 'like', 'using', 'called', 'example'
}

# Technical patterns for generating YouTube search phrases
TECHNICAL_PATTERNS = [
    r'\b[A-Z][a-zA-Z]*\s+[A-Z][a-zA-Z]*\b',  # Product names (e.g., "Visual Studio")
    r'\b\w+\.py\b',  # File names
    r'\b\w+ing\b',  # Actions (e.g., "programming", "coding")
]

# ============================================================================
# B-roll Result Filtering Constants
# ============================================================================
#
# Note: we deliberately do NOT inject words like "b-roll" or "footage" into the
# search query itself. Searching for those labels surfaces generic self-labeled
# "B-Roll" compilation packs that are usually irrelevant to the topic. Relevance
# is steered on the result side (below) instead, by demoting talking-head titles.

# Title substrings that signal talking-head / non-B-roll content. Matching
# candidates are heavily penalized during ranking so they sink below usable
# footage (they are not hard-removed, to avoid returning nothing for niche
# queries).
TALKING_HEAD_TITLE_PATTERNS = [
    'interview', 'podcast', 'reaction', 'explained', 'explainer', 'review',
    'vlog', 'episode', 'lecture', ' talk', 'press conference', 'debate',
    'q&a', 'q & a', 'tutorial', 'how to', "let's play", 'lets play',
    'livestream', 'live stream', 'speech', 'testimony', 'news', 'documentary',
    'ft.', 'feat.', 'commentary', 'reacts', 'analysis', 'breakdown',
]

# Title substrings that signal genuinely visual footage. Matching candidates are
# mildly boosted during ranking. Intentionally excludes "b-roll"/"footage"/
# "stock"/"no copyright" - those labels correlate with low-value generic packs;
# we keep only descriptors of what the footage actually looks like.
BROLL_TITLE_BOOST_PATTERNS = [
    'cinematic', '4k', '1080p', 'timelapse', 'time lapse', 'aerial', 'drone',
    'ambience', 'ambient', 'relaxing', 'scenery', 'establishing shot',
    'montage', 'slow motion', 'nature',
]

# Per-match weights for ranking YouTube candidates.
TALKING_HEAD_PENALTY = 5.0
BROLL_BOOST = 3.0

# Acceptable duration bounds (seconds) for YouTube B-roll candidates. Results
# outside this range are dropped before ranking (unless that would leave no
# candidates). Unknown/zero durations are allowed through.
MIN_YOUTUBE_DURATION = 12
MAX_YOUTUBE_DURATION = 1200

# ============================================================================
# LLM Query Generation Constants
# ============================================================================

# Default Gemini model used for visual B-roll query generation. Overridable via
# the GEMINI_MODEL environment variable.
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"

# Timeout (seconds) for Gemini API requests.
GEMINI_REQUEST_TIMEOUT = 30

# ============================================================================
# Game B-roll Skeleton Constants (chaptered-gameplay pipeline)
# ============================================================================

# Search templates used to discover chaptered source videos for a game. These
# target human-labeled corpora (walkthroughs, boss compilations) whose chapter
# markers are ground truth for "what's on screen".
CHAPTER_SOURCE_QUERY_TEMPLATES = [
    "{game} all bosses",
    "{game} all cutscenes",
    "{game} walkthrough no commentary",
    "{game} 100% walkthrough",
]

# Flat search results to consider per source query.
CHAPTER_SEARCH_RESULTS_PER_QUERY = 5

# Cap on full metadata fetches (chapters live in per-video metadata, which is
# one network round-trip each; flat search results do not include them).
CHAPTER_MAX_SOURCE_VIDEOS = 8

# Source videos need at least this many chapters to be a useful labeled corpus.
CHAPTER_MIN_CHAPTERS = 3

# Ignore source videos shorter than this (seconds) - chaptered walkthroughs and
# compilations are long; short videos are rarely labeled corpora.
CHAPTER_MIN_SOURCE_DURATION = 600

# Fuzzy-match score (0-100) required for an entity to claim a chapter title.
CHAPTER_MATCH_THRESHOLD = 70

# Candidate-variety trick: alternates within one chapter start this many
# seconds apart, so at least one offset tends to avoid walk-up/menu moments.
CHAPTER_OFFSET_STEP_SECONDS = 8.0

# Downloaded clip windows are cut loose (window = beat duration + slack, with a
# floor) so the editor can slide the in-point instead of re-fetching.
CHAPTER_WINDOW_MIN_SECONDS = 9.0
CHAPTER_WINDOW_SLACK_SECONDS = 4.0

# Candidates fetched per game-entity beat (the human picks among these).
GAME_CANDIDATES_PER_BEAT = 3

# Fandom (game wiki) API endpoint and request timeout for labeled stills.
FANDOM_API_URL = "https://{subdomain}.fandom.com/api.php"
WIKI_REQUEST_TIMEOUT = 15

# File extensions treated as still images by the timeline generator.
STILL_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'}

# ============================================================================
# VO Conform Constants (voiceover-first timing)
# ============================================================================

# Default faster-whisper model for VO transcription. Overridable via --whisper-model.
VO_WHISPER_MODEL = "small.en"
VO_WHISPER_DEVICE = "cpu"
VO_WHISPER_COMPUTE = "int8"

# A beat counts as "found in the VO" when at least this fraction of its script
# tokens match transcript words (reworded lines still anchor on their nouns).
VO_MIN_BEAT_COVERAGE = 0.35

# Below this overall script-token match ratio the audio is treated as the
# wrong file entirely and conform aborts instead of producing garbage cuts.
VO_MIN_OVERALL_COVERAGE = 0.5

# Warn when this many seconds of unscripted speech sit between two beats
# (likely an ad-lib or a retake the creator should check).
VO_ADLIB_GAP_WARN_SECONDS = 4.0
