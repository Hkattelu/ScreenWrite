# Requirements Document: screenwrite

## Introduction

screenwrite is a CLI tool that automates the creation of video timelines for DaVinci Resolve. It takes a markdown video script as input, parses it into logical "beats" (5-10 second segments), generates contextual search queries for B-roll footage, automatically fetches video assets from YouTube and Pexels, and generates a Final Cut Pro XML (FCPXML) timeline that can be imported directly into DaVinci Resolve. The system orchestrates multiple componentsâ€”script parsing, asset fetching, and XML generationâ€”to produce a production-ready timeline with voiceover placeholders and synchronized B-roll clips.

## Glossary

- **Beat**: A logical segment of a video script, typically 5-10 seconds of narration or content
- **B-Roll**: Supporting video footage (stock footage, YouTube clips) that accompanies the main narrative
- **A-Roll**: Primary voiceover or narration track (represented as gaps/placeholders in the timeline)
- **FCPXML**: Final Cut Pro XML format, a standardized timeline format compatible with DaVinci Resolve and Final Cut Pro
- **Stock Keyword**: A descriptive phrase used to search stock footage libraries (e.g., "person typing on keyboard")
- **YouTube Search Phrase**: A specific search query used to find relevant footage on YouTube (e.g., "Final Fantasy VII original gameplay menu")
- **Clip**: A video segment with defined in/out points and duration
- **Gap**: A placeholder segment on the timeline representing voiceover or narration space
- **Connected Clip**: A clip attached to a specific lane in FCPXML, positioned relative to a gap or other clip
- **Spine**: The primary timeline track containing gaps and primary clips
- **Lane**: Secondary tracks in FCPXML where B-roll clips are placed
- **Resolve**: DaVinci Resolve, professional video editing software
- **Markdown Script**: A text file in markdown format containing the video script with structural markers (headers, sections)
- **Query Generation**: The process of creating search terms from script content to find appropriate B-roll footage
- **Asset Fetching**: The process of downloading video files from external sources (YouTube, Pexels)
- **Orchestrator**: The main coordinator component that manages the workflow of parsing, fetching, and generating

## Requirements

### Requirement 1

**User Story:** As a video creator, I want to convert a markdown script into a structured video timeline, so that I can quickly produce video content without manually searching for and organizing B-roll footage.

#### Acceptance Criteria

1. WHEN a user provides a markdown script file THEN the system SHALL parse the file and identify logical beats of 5-10 seconds each
2. WHEN a beat is identified THEN the system SHALL generate a stock footage keyword describing the beat content
3. WHEN a beat is identified THEN the system SHALL generate a YouTube search phrase relevant to the beat content
4. WHEN beats are generated THEN the system SHALL create a Beat dataclass instance for each beat containing: id, text, duration, stock_keyword, youtube_search_phrase, and asset paths
5. WHEN a Beat is created THEN the system SHALL automatically calculate the duration based on word count using a heuristic of 2.5 words per second

### Requirement 2

**User Story:** As a video creator, I want the system to automatically fetch B-roll footage from multiple sources, so that I don't have to manually download and organize video assets.

#### Acceptance Criteria

1. WHEN a beat requires B-roll footage THEN the system SHALL attempt to fetch a video from YouTube using the YouTube search phrase
2. WHEN YouTube fetching fails or is unavailable THEN the system SHALL fallback to fetching from Pexels API
3. WHEN fetching from YouTube THEN the system SHALL use yt-dlp to search and download the first matching result
4. WHEN a video is downloaded THEN the system SHALL trim it to match the beat duration using ffmpeg
5. WHEN fetching from Pexels THEN the system SHALL use the Pexels API with the stock keyword to find matching video
6. WHEN an API key is missing or rate limits are exceeded THEN the system SHALL handle the error gracefully and continue processing

### Requirement 3

**User Story:** As a video editor, I want the system to generate a valid FCPXML timeline that imports into DaVinci Resolve, so that I can immediately begin editing with the B-roll already synchronized.

#### Acceptance Criteria

1. WHEN all beats and assets are processed THEN the system SHALL generate a valid FCPXML 1.8 document
2. WHEN generating FCPXML THEN the system SHALL create a primary spine track containing gaps matching each beat duration
3. WHEN generating FCPXML THEN the system SHALL create connected clips on Lane 1 for each B-roll asset, aligned to the corresponding beat
4. WHEN generating FCPXML THEN the system SHALL include proper resource references for all video files
5. WHEN FCPXML is generated THEN the system SHALL write the output to a specified file path
6. WHEN FCPXML is generated THEN the system SHALL validate the XML structure before writing

### Requirement 4

**User Story:** As a user, I want a command-line interface to control the entire workflow, so that I can automate video timeline generation from scripts.

#### Acceptance Criteria

1. WHEN the user runs the CLI tool THEN the system SHALL accept a markdown script file path as input
2. WHEN the user runs the CLI tool THEN the system SHALL accept an output file path for the FCPXML timeline
3. WHEN the user runs the CLI tool THEN the system SHALL accept optional API keys (Pexels) as arguments or environment variables
4. WHEN the user runs the CLI tool THEN the system SHALL display clear error messages for missing required files or invalid arguments
5. WHEN the user runs the CLI tool THEN the system SHALL provide help text describing all available options

### Requirement 5

**User Story:** As a video editor, I want the system to optionally integrate with DaVinci Resolve, so that I can import the timeline and assets directly into an open project.

#### Acceptance Criteria

1. WHERE Resolve integration is enabled THEN the system SHALL create a new bin in the open Resolve project
2. WHERE Resolve integration is enabled THEN the system SHALL import all downloaded B-roll assets into the bin
3. WHERE Resolve integration is enabled THEN the system SHALL import the generated FCPXML timeline into the project
4. WHERE Resolve integration is not available THEN the system SHALL complete the workflow without errors and save the FCPXML file

### Requirement 6

**User Story:** As a developer, I want the system to be modular and extensible, so that I can add new asset sources or modify the parsing logic without affecting other components.

#### Acceptance Criteria

1. WHEN the system is designed THEN the system SHALL separate concerns into distinct modules: parsing, fetching, XML generation, and orchestration
2. WHEN a new asset fetcher is added THEN the system SHALL integrate with the existing orchestrator without modifying core logic
3. WHEN the parsing logic is updated THEN the system SHALL not affect the fetching or XML generation components
4. WHEN the XML generation is modified THEN the system SHALL not affect the parsing or fetching components

### Requirement 7

**User Story:** As a user, I want the system to handle errors gracefully, so that missing APIs, network issues, or invalid input don't crash the application.

#### Acceptance Criteria

1. WHEN a network error occurs during asset fetching THEN the system SHALL log the error and continue processing remaining beats
2. WHEN an API key is missing THEN the system SHALL skip that fetcher and try alternatives
3. WHEN ffmpeg is not installed THEN the system SHALL handle the error gracefully and skip video trimming
4. WHEN a markdown file is invalid or malformed THEN the system SHALL provide a clear error message indicating the issue
5. WHEN an output directory does not exist THEN the system SHALL create it or provide a clear error message


