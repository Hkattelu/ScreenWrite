# Design Document: vid-orchestrator

## Overview

vid-orchestrator is a modular Python CLI tool that orchestrates the conversion of markdown video scripts into DaVinci Resolve-compatible FCPXML timelines with auto-fetched B-roll. The system follows a pipeline architecture with four main stages:

1. **Script Parsing**: Convert markdown into structured beats with metadata
2. **Asset Fetching**: Download B-roll from YouTube or Pexels
3. **XML Generation**: Create FCPXML timeline with gaps and connected clips
4. **Orchestration**: Coordinate all stages and provide CLI interface

The design prioritizes modularity, allowing each component to be developed, tested, and extended independently while maintaining clear interfaces between stages.

## Architecture

### High-Level Pipeline

```
Markdown Script
    ↓
[Script Parser] → Beat objects with queries
    ↓
[Asset Fetchers] → Downloaded video files
    ↓
[XML Generator] → FCPXML timeline
    ↓
[Orchestrator] → Output file + optional Resolve import
```

### Module Structure

```
vid_orchestrator/
├── core/
│   ├── __init__.py
│   └── beat.py                 # Beat dataclass
├── parsing/
│   ├── __init__.py
│   └── script_parser.py        # Markdown → beats
├── fetchers/
│   ├── __init__.py
│   ├── base_fetcher.py         # Abstract base class
│   ├── youtube_client.py       # yt-dlp wrapper
│   └── pexels_client.py        # Pexels API client
├── generators/
│   ├── __init__.py
│   └── xml_generator.py        # FCPXML builder
├── orchestrator.py             # Main coordinator
├── cli.py                      # CLI interface
├── resolve_integration.py      # Resolve fusionscript wrapper
└── utils.py                    # Shared utilities (logging, etc.)
```

### Dependency Graph

```
Beat (core)
  ↑
  ├─ ScriptParser (parsing)
  ├─ YouTubeClient (fetchers)
  ├─ PexelsClient (fetchers)
  └─ XMLGenerator (generators)
       ↑
       └─ VideoOrchestrator (orchestrator)
            ↑
            ├─ CLI (cli)
            └─ ResolveIntegration (resolve_integration)
```

## Components and Interfaces

### 1. Beat Dataclass (core/beat.py)

**Purpose**: Represent a single logical segment of the video script.

**Fields**:
- `id: str` - Unique identifier (e.g., "beat_001")
- `text: str` - The actual script text for this beat
- `duration: float` - Duration in seconds (auto-calculated)
- `stock_keyword: str` - Search term for stock footage
- `youtube_search_phrase: str` - Search term for YouTube
- `asset_paths: Dict[str, str]` - Mapping of fetcher names to downloaded file paths

**Methods**:
- `__post_init__()` - Auto-calculate duration from word count (2.5 wps heuristic)
- `validate()` - Ensure duration is 5-10 seconds, text is non-empty

**Example**:
```python
beat = Beat(
    id="beat_001",
    text="A person sits at a desk typing code...",
    stock_keyword="person typing on keyboard",
    youtube_search_phrase="programmer coding tutorial"
)
# duration auto-calculated to ~6 seconds
```

### 2. ScriptParser (parsing/script_parser.py)

**Purpose**: Parse markdown files into Beat objects.

**Key Methods**:
- `parse(file_path: str) -> List[Beat]` - Main entry point
- `_chunk_text(text: str, target_duration: float) -> List[str]` - Split text into beats
- `_generate_stock_keyword(text: str) -> str` - Create stock footage keyword
- `_generate_youtube_phrase(text: str) -> str` - Create YouTube search phrase

**Algorithm**:
1. Read markdown file
2. Extract section headers (# and ##) as context
3. Split body text into chunks targeting 5-10 seconds each
4. For each chunk, generate stock keyword and YouTube phrase
5. Create Beat objects with auto-calculated durations

**Edge Cases**:
- Very short sections (< 5 seconds)
- Very long sections (> 10 seconds) - split into multiple beats
- Special characters in text
- Empty sections

### 3. Asset Fetchers (fetchers/)

**Base Interface** (base_fetcher.py):
```python
class AssetFetcher(ABC):
    @abstractmethod
    def fetch(self, query: str, duration: float) -> Optional[str]:
        """Fetch asset matching query, return file path or None"""
        pass
```

#### YouTubeClient (fetchers/youtube_client.py)

**Purpose**: Download B-roll from YouTube using yt-dlp.

**Key Methods**:
- `fetch(query: str, duration: float) -> Optional[str]` - Search and download
- `_search(query: str) -> Optional[str]` - Get first result URL
- `_download(url: str, duration: float) -> str` - Download and trim using ffmpeg
- `_trim_video(input_path: str, duration: float) -> str` - Trim to exact duration

**Behavior**:
- Search YouTube for query
- Download first result as mp4
- Trim to beat duration using ffmpeg
- Return file path or None on failure

**Error Handling**:
- Network errors → log and return None
- ffmpeg not installed → log warning and return untrimmed file
- No results found → log and return None

#### PexelsClient (fetchers/pexels_client.py)

**Purpose**: Fetch B-roll from Pexels API (free tier).

**Key Methods**:
- `fetch(query: str, duration: float) -> Optional[str]` - Search and download
- `_search(query: str) -> Optional[Dict]` - Query Pexels API
- `_download(url: str) -> str` - Download video file

**Behavior**:
- Search Pexels API with stock keyword
- Download first matching video
- Return file path or None on failure

**Error Handling**:
- Missing API key → log and return None
- Rate limit exceeded → log and return None
- Network errors → log and return None

### 4. XMLGenerator (generators/xml_generator.py)

**Purpose**: Generate FCPXML 1.8 timeline with gaps and connected clips.

**Key Methods**:
- `generate(beats: List[Beat], asset_map: Dict[str, str]) -> str` - Main entry point
- `_create_root() -> Element` - Initialize FCPXML root
- `_create_format() -> Element` - Define video format (1920x1080, 30fps)
- `_create_resources(asset_map: Dict[str, str]) -> Element` - Register video files
- `_create_spine(beats: List[Beat]) -> Element` - Create primary track with gaps
- `_create_connected_clips(beats: List[Beat], asset_map: Dict[str, str]) -> Element` - Create B-roll on Lane 1
- `_validate_xml(root: Element) -> bool` - Validate structure
- `write(root: Element, output_path: str)` - Write to file

**FCPXML Structure**:
```xml
<fcpxml version="1.8">
  <resources>
    <format id="r1" name="1920x1080 30fps" />
    <media id="r2" name="video1.mp4" ... />
  </resources>
  <library>
    <event name="Timeline">
      <project name="Project">
        <sequence format="r1">
          <spine>
            <gap duration="150" /> <!-- 5 seconds at 30fps -->
            <gap duration="180" /> <!-- 6 seconds -->
          </spine>
          <lane index="1">
            <clip ref="r2" duration="150" offset="0" />
            <clip ref="r3" duration="180" offset="150" />
          </lane>
        </sequence>
      </project>
    </event>
  </library>
</fcpxml>
```

**Timing Calculation**:
- FCPXML uses frame counts (30fps assumed)
- Duration in seconds × 30 = frame count
- Offset calculated as cumulative sum of previous beat durations

### 5. VideoOrchestrator (orchestrator.py)

**Purpose**: Coordinate all components and manage workflow.

**Key Methods**:
- `orchestrate(script_path: str, output_path: str, config: Dict) -> bool` - Main workflow
- `_parse_script(script_path: str) -> List[Beat]` - Parse markdown
- `_fetch_assets(beats: List[Beat]) -> Dict[str, str]` - Download B-roll
- `_generate_timeline(beats: List[Beat], asset_map: Dict[str, str]) -> str` - Generate FCPXML
- `_import_to_resolve(fcpxml_path: str, assets: Dict[str, str])` - Optional Resolve import

**Workflow**:
1. Parse script into beats
2. Fetch assets for each beat (YouTube → Pexels fallback)
3. Generate FCPXML timeline
4. Optionally import to Resolve
5. Return success/failure status

**Error Handling**:
- Catch exceptions at each stage
- Log errors with context
- Continue processing on non-critical failures
- Return detailed status report

### 6. CLI Interface (cli.py)

**Purpose**: Provide command-line interface for users.

**Arguments**:
- `script` (positional) - Path to markdown script file
- `--output` - Output FCPXML file path (default: output.fcpxml)
- `--pexels-key` - Pexels API key (or env var PEXELS_API_KEY)
- `--resolve` - Enable Resolve integration (optional)
- `--no-fetch` - Skip asset fetching (generate empty timeline)
- `--verbose` - Enable debug logging

**Example Usage**:
```bash
python -m vid_orchestrator script.md --output timeline.fcpxml --pexels-key YOUR_KEY
```

### 7. Resolve Integration (resolve_integration.py)

**Purpose**: Optional integration with DaVinci Resolve via fusionscript.

**Key Methods**:
- `import_to_resolve(fcpxml_path: str, assets: Dict[str, str]) -> bool` - Import timeline and assets
- `_create_bin(name: str) -> bool` - Create new bin in project
- `_import_media(bin_id: str, file_paths: List[str]) -> bool` - Import media files
- `_import_timeline(fcpxml_path: str) -> bool` - Import FCPXML

**Behavior**:
- Connect to running Resolve instance
- Create bin for assets
- Import all downloaded videos
- Import FCPXML timeline
- Return success/failure

**Error Handling**:
- Resolve not running → log and skip
- Fusionscript not available → log and skip
- Import errors → log and continue

## Data Models

### Beat

```python
@dataclass
class Beat:
    id: str
    text: str
    stock_keyword: str
    youtube_search_phrase: str
    duration: float = field(init=False)
    asset_paths: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        # Auto-calculate duration: 2.5 words per second
        word_count = len(self.text.split())
        self.duration = word_count / 2.5
        self.validate()
    
    def validate(self):
        assert 5 <= self.duration <= 10, f"Duration {self.duration} not in 5-10 second range"
        assert self.text.strip(), "Text cannot be empty"
```

### Asset Map

```python
# Dict[beat_id, Dict[fetcher_name, file_path]]
asset_map = {
    "beat_001": {
        "youtube": "/tmp/beat_001_youtube.mp4",
        "pexels": None  # Failed to fetch
    },
    "beat_002": {
        "youtube": None,
        "pexels": "/tmp/beat_002_pexels.mp4"
    }
}
```

### Configuration

```python
@dataclass
class Config:
    pexels_api_key: Optional[str] = None
    youtube_enabled: bool = True
    pexels_enabled: bool = True
    resolve_enabled: bool = False
    output_dir: str = "./output"
    verbose: bool = False
```

## Error Handling

### Error Categories

1. **Input Errors** (user responsibility)
   - Missing script file → Clear error message with path
   - Invalid markdown → Parse error with line number
   - Invalid output path → Directory creation or error

2. **Network Errors** (graceful degradation)
   - YouTube unavailable → Skip to Pexels
   - Pexels rate limit → Skip fetching, continue
   - Connection timeout → Log and retry once

3. **System Errors** (graceful degradation)
   - ffmpeg not installed → Skip trimming, use full video
   - Resolve not running → Skip import, save FCPXML
   - Insufficient disk space → Log and fail gracefully

### Error Logging

- All errors logged with timestamp, component, and context
- Warnings for non-critical failures (e.g., missing API key)
- Errors for critical failures (e.g., invalid script)
- Debug logs for troubleshooting

## Testing Strategy

### Unit Testing

Unit tests verify specific examples and edge cases:

- **Beat dataclass**: Duration calculation, validation, edge cases
- **ScriptParser**: Parsing logic, chunk splitting, keyword generation
- **YouTubeClient**: yt-dlp wrapper (mocked), error handling
- **PexelsClient**: API client (mocked), error handling
- **XMLGenerator**: XML structure, timing calculations, validation
- **Orchestrator**: Coordinator logic, error handling
- **CLI**: Argument parsing, help text, error messages

### Property-Based Testing

Property-based tests verify universal properties that should hold across all inputs:

- **Beat duration consistency**: Duration always 5-10 seconds
- **Round-trip parsing**: Parse → serialize → parse produces equivalent beats
- **XML structure validity**: Generated FCPXML always valid
- **Asset mapping completeness**: All beats have asset entries
- **Timing accuracy**: Cumulative beat durations match timeline length

### Testing Framework

- **Unit Tests**: pytest with fixtures for common test data
- **Property Tests**: hypothesis for property-based testing
- **Mocking**: unittest.mock for external APIs (YouTube, Pexels)
- **Coverage Target**: 80%+ overall, 90%+ for core modules

### Test Organization

```
tests/
├── unit/
│   ├── test_beat.py
│   ├── test_script_parser.py
│   ├── test_youtube_client.py
│   ├── test_pexels_client.py
│   ├── test_xml_generator.py
│   ├── test_orchestrator.py
│   └── test_cli.py
├── integration/
│   ├── test_end_to_end.py
│   └── test_resolve_integration.py
├── fixtures/
│   ├── sample_script.md
│   ├── expected_output.fcpxml
│   └── mock_responses.json
└── conftest.py
```

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Beat Duration Bounds

*For any* markdown script, all generated beats SHALL have durations between 5 and 10 seconds (inclusive).

**Validates: Requirements 1.1, 1.5**

**Rationale**: The core requirement is that beats are 5-10 seconds. This property ensures the duration calculation heuristic (2.5 words per second) produces valid beats. We generate random markdown text with varying word counts and verify all resulting beats fall within the valid range.

### Property 2: Beat Completeness

*For any* beat generated from markdown text, the Beat dataclass instance SHALL contain all required fields: id, text, duration, stock_keyword, youtube_search_phrase, and asset_paths.

**Validates: Requirements 1.4**

**Rationale**: The Beat dataclass must have all required fields for downstream processing. We generate beats and verify all fields are present and properly initialized.

### Property 3: Duration Calculation Accuracy

*For any* text with a known word count, the Beat duration SHALL equal word_count / 2.5 (within 0.1 second tolerance).

**Validates: Requirements 1.5**

**Rationale**: The duration calculation uses a specific heuristic. We generate text with known word counts and verify the calculation is correct.

### Property 4: Query Generation Non-Emptiness

*For any* beat text, both the stock_keyword and youtube_search_phrase SHALL be non-empty strings.

**Validates: Requirements 1.2, 1.3**

**Rationale**: Query generation must produce valid search terms. We generate random beat text and verify both queries are non-empty.

### Property 5: YouTube Fetcher Invocation

*For any* beat with a YouTube search phrase, the YouTube fetcher SHALL be invoked with that phrase as the search query.

**Validates: Requirements 2.1, 2.3**

**Rationale**: The YouTube client must be called with the correct query. We mock yt-dlp and verify it's called with the YouTube search phrase.

### Property 6: Fallback to Pexels

*For any* beat where YouTube fetching fails, the Pexels fetcher SHALL be invoked as a fallback.

**Validates: Requirements 2.2**

**Rationale**: The system must gracefully degrade to Pexels when YouTube fails. We mock YouTube to fail and verify Pexels is called.

### Property 7: Pexels Fetcher Invocation

*For any* beat with a stock keyword, the Pexels fetcher SHALL be invoked with that keyword as the search query.

**Validates: Requirements 2.5**

**Rationale**: The Pexels client must be called with the correct query. We mock the Pexels API and verify it's called with the stock keyword.

### Property 8: Video Trimming

*For any* downloaded video, ffmpeg SHALL be invoked to trim the video to the beat duration.

**Validates: Requirements 2.4**

**Rationale**: Downloaded videos must be trimmed to match beat duration. We mock ffmpeg and verify it's called with the correct duration.

### Property 9: Error Handling Continuity

*For any* beat where asset fetching fails, the orchestrator SHALL continue processing remaining beats without stopping.

**Validates: Requirements 2.6, 7.1, 7.2**

**Rationale**: The system must be resilient to failures. We simulate fetch failures and verify processing continues.

### Property 10: FCPXML Validity

*For any* set of beats and assets, the generated FCPXML document SHALL be valid XML that can be parsed without errors.

**Validates: Requirements 3.1**

**Rationale**: The generated FCPXML must be well-formed. We generate FCPXML and verify it parses correctly.

### Property 11: Spine Gap Completeness

*For any* set of beats, the FCPXML spine SHALL contain exactly one gap for each beat, with duration matching the beat duration.

**Validates: Requirements 3.2**

**Rationale**: The spine must have gaps for all beats. We generate FCPXML and verify gaps match beats.

### Property 12: Connected Clips Alignment

*For any* beat with a fetched asset, the FCPXML SHALL contain a connected clip on Lane 1 with duration matching the beat duration and offset matching the cumulative duration of previous beats.

**Validates: Requirements 3.3**

**Rationale**: Connected clips must be properly aligned in time. We generate FCPXML and verify clip timing and positioning.

### Property 13: Resource Reference Validity

*For any* clip in the FCPXML, the resource reference SHALL point to a valid resource defined in the resources section.

**Validates: Requirements 3.4**

**Rationale**: All clips must reference valid resources. We generate FCPXML and verify all references are valid.

### Property 14: File Output Existence

*For any* FCPXML generation, the output file SHALL be written to the specified file path and be readable.

**Validates: Requirements 3.5**

**Rationale**: The FCPXML must be written to disk. We generate FCPXML and verify the file exists and is readable.

### Property 15: CLI Argument Acceptance

*For any* valid markdown script path and output path, the CLI SHALL accept both as arguments without error.

**Validates: Requirements 4.1, 4.2**

**Rationale**: The CLI must accept required arguments. We run the CLI with various valid inputs and verify acceptance.

### Property 16: Environment Variable Support

*For any* API key provided via environment variable, the CLI SHALL use that key for the corresponding fetcher.

**Validates: Requirements 4.3**

**Rationale**: The CLI must support environment variables for API keys. We set environment variables and verify they're used.

### Property 17: Error Message Clarity

*For any* invalid input to the CLI, the system SHALL display an error message that clearly indicates the problem.

**Validates: Requirements 4.4, 7.4, 7.5**

**Rationale**: Error messages must be helpful. We provide invalid inputs and verify error messages are clear.

### Property 18: Help Text Availability

*When* the CLI is run with the --help flag, the system SHALL display help text describing all available options.

**Validates: Requirements 4.5**

**Rationale**: Users must be able to discover CLI options. We run --help and verify help text is displayed.

### Property 19: Resolve Bin Creation

*For any* beat set where Resolve integration is enabled, the system SHALL create a new bin in the Resolve project.

**Validates: Requirements 5.1**

**Rationale**: Resolve integration must create bins. We mock Resolve and verify bin creation is called.

### Property 20: Resolve Asset Import

*For any* downloaded asset where Resolve integration is enabled, the system SHALL import that asset into the Resolve bin.

**Validates: Requirements 5.2**

**Rationale**: All assets must be imported to Resolve. We mock Resolve and verify media import is called for all assets.

### Property 21: Resolve Timeline Import

*For any* generated FCPXML where Resolve integration is enabled, the system SHALL import the timeline into the Resolve project.

**Validates: Requirements 5.3**

**Rationale**: The FCPXML must be imported to Resolve. We mock Resolve and verify FCPXML import is called.

### Property 22: Graceful Degradation Without Resolve

*For any* beat set where Resolve integration is disabled or unavailable, the system SHALL complete the workflow and save the FCPXML file without errors.

**Validates: Requirements 5.4**

**Rationale**: The system must work without Resolve. We disable Resolve and verify the workflow completes and saves the file.

### Property 23: Missing API Key Handling

*For any* beat where an API key is missing, the system SHALL skip that fetcher and attempt alternatives.

**Validates: Requirements 7.2**

**Rationale**: Missing API keys must not crash the system. We omit API keys and verify alternatives are tried.

### Property 24: FFmpeg Unavailability Handling

*For any* downloaded video where ffmpeg is unavailable, the system SHALL handle the error gracefully and continue processing.

**Validates: Requirements 7.3**

**Rationale**: Missing ffmpeg must not crash the system. We mock ffmpeg to be unavailable and verify graceful handling.

### Property 25: Output Directory Creation

*For any* non-existent output directory path, the system SHALL either create the directory or provide a clear error message.

**Validates: Requirements 7.5**

**Rationale**: The system must handle missing directories. We specify non-existent paths and verify creation or clear errors.

## Error Handling

### Error Categories and Responses

**Input Validation Errors**:
- Invalid markdown syntax → Parse error with line number and context
- Missing required files → FileNotFoundError with helpful path suggestion
- Invalid output path → OSError with suggestion to create directory

**Network Errors**:
- YouTube search fails → Log warning, try Pexels
- Pexels API fails → Log warning, skip asset
- Connection timeout → Retry once, then skip

**System Errors**:
- ffmpeg not installed → Log warning, skip trimming
- Insufficient disk space → Log error, fail gracefully
- Resolve not running → Log info, skip import

**API Errors**:
- Missing API key → Log info, skip fetcher
- Rate limit exceeded → Log warning, skip fetcher
- Invalid API response → Log error, skip asset

### Logging Strategy

- **DEBUG**: Detailed execution flow (parsing steps, API calls)
- **INFO**: Workflow progress (beats parsed, assets fetched)
- **WARNING**: Non-critical failures (missing API key, network timeout)
- **ERROR**: Critical failures (invalid script, file I/O error)

All logs include timestamp, component name, and context for debugging.

