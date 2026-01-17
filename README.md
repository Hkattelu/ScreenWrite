# vid-orchestrator

A Python CLI tool that automates video timeline creation from markdown scripts with automatic B-roll footage fetching.

## Overview

vid-orchestrator converts markdown video scripts into DaVinci Resolve-compatible FCPXML timelines with automatically fetched B-roll footage from YouTube and Pexels. It parses your script, breaks it into timed segments (beats), generates search queries, fetches relevant video clips, and outputs a complete timeline ready for editing.

## Features

- **Markdown Script Parsing** - Write your video script in plain markdown with natural language
- **Automatic Beat Generation** - Text is chunked into 5-10 second segments based on word count (2.5 words/second heuristic)
- **Smart B-roll Query Generation** - Auto-generates stock footage keywords and YouTube search phrases from your content
- **Multi-Source Asset Fetching** - Downloads B-roll from YouTube (via yt-dlp) and Pexels (stock footage)
- **FCPXML 1.8 Timeline Generation** - Creates industry-standard timelines compatible with DaVinci Resolve and Final Cut Pro
- **DaVinci Resolve Integration** - Optional direct import into Resolve projects
- **Comprehensive Error Handling** - Graceful degradation with detailed logging and retry logic

## Installation

### Prerequisites

- Python 3.7+
- ffmpeg (for video trimming)
- yt-dlp (for YouTube downloads)
- Optional: DaVinci Resolve (for direct import)

### Install Dependencies

```powershell
# Install Python dependencies
pip install yt-dlp requests

# Install ffmpeg (Windows)
# Download from https://ffmpeg.org/download.html
# Or using Chocolatey:
choco install ffmpeg

# Install yt-dlp (if not already installed)
pip install --upgrade yt-dlp
```

### Setup

```powershell
# Clone or download the repository
cd C:\Users\himan\code\footage

# Set Pexels API key (optional, for stock footage)
$env:PEXELS_API_KEY = "your_pexels_api_key_here"
```

## Quick Start

### Basic Usage

```powershell
# Convert a markdown script to FCPXML timeline
python -m vid_orchestrator script.md --output timeline.fcpxml

# With Pexels API key
python -m vid_orchestrator script.md --output timeline.fcpxml --pexels-key YOUR_KEY

# Skip asset fetching (generate empty timeline)
python -m vid_orchestrator script.md --output timeline.fcpxml --no-fetch

# Enable verbose logging
python -m vid_orchestrator script.md --output timeline.fcpxml --verbose
```

### Example Workflow

1. **Write your script** in markdown format:

```markdown
# Python Tutorial: Getting Started

## Introduction
Welcome to this Python programming tutorial. We'll learn the fundamentals of Python development and write our first program together.

## Setting Up Your Environment
First, visit the official Python website and download the latest version. The installation process is straightforward and takes just a few minutes to complete.
```

2. **Run vid-orchestrator**:

```powershell
python -m vid_orchestrator tutorial.md --output tutorial.fcpxml --pexels-key YOUR_KEY --verbose
```

3. **Import into DaVinci Resolve**:
   - Open DaVinci Resolve
   - File → Import → Timeline → Select `tutorial.fcpxml`
   - Your timeline is ready with B-roll clips aligned to your script segments

## Architecture

### Components

1. **ScriptParser** (`vid_orchestrator/parsing/script_parser.py`)
   - Parses markdown files
   - Extracts headers for context
   - Chunks text into 5-10 second beats
   - Generates search queries for each beat

2. **Beat** (`vid_orchestrator/core/beat.py`)
   - Dataclass representing a video segment
   - Contains text, duration, stock keyword, and YouTube search phrase
   - Auto-calculates duration from word count

3. **AssetOrchestrator** (`vid_orchestrator/fetchers/asset_orchestrator.py`)
   - Coordinates multiple asset fetchers
   - Implements YouTube → Pexels fallback strategy
   - Batch processing for efficiency

4. **YouTubeClient** (`vid_orchestrator/fetchers/youtube_client.py`)
   - Searches and downloads from YouTube via yt-dlp
   - Trims videos to target duration using ffmpeg

5. **PexelsClient** (`vid_orchestrator/fetchers/pexels_client.py`)
   - Fetches stock footage from Pexels API
   - Handles rate limiting and API errors

6. **XMLGenerator** (`vid_orchestrator/generators/xml_generator.py`)
   - Creates FCPXML 1.8 documents
   - Generates spine track with gaps (voiceover placeholders)
   - Creates connected clips lane for B-roll

7. **VideoOrchestrator** (`vid_orchestrator/orchestrator.py`)
   - Main coordinator for the complete workflow
   - Manages parse → fetch → generate pipeline

8. **CLI** (`vid_orchestrator/cli.py`)
   - Command-line interface with comprehensive argument parsing
   - Input validation and error reporting

### Workflow

```
Markdown Script
      ↓
[ScriptParser] → Beats (5-10s segments with queries)
      ↓
[AssetOrchestrator] → Downloaded B-roll videos
      ↓
[XMLGenerator] → FCPXML timeline
      ↓
[ResolveIntegration] → DaVinci Resolve (optional)
```

## Markdown Script Format

See [Markdown Script Specification](#markdown-script-specification) below for complete details.

### Basic Structure

- Use `#` and `##` headers for context and organization
- Write body text in natural, conversational language
- Include specific visual keywords (software names, actions, UI elements)
- Target 13-25 words per intended beat (5-10 seconds)

### Example

```markdown
# Web Development Tutorial

## Setting Up Your Environment
Download and install Node.js from the official website. Open your terminal and verify the installation by typing 'node --version'.

## Creating Your First Project
Navigate to your project folder and initialize a new Node.js project. Create an index.html file and open it in your browser.
```

## CLI Reference

### Command Syntax

```
python -m vid_orchestrator SCRIPT [OPTIONS]
```

### Arguments

- `SCRIPT` - Path to the markdown script file (required)

### Options

- `--output`, `-o` - Output FCPXML file path (default: output.fcpxml)
- `--pexels-key` - Pexels API key (or set PEXELS_API_KEY environment variable)
- `--resolve` - Enable DaVinci Resolve integration
- `--no-fetch` - Skip asset fetching and generate empty timeline
- `--verbose`, `-v` - Enable verbose debug logging
- `--output-dir` - Directory for temporary files and downloaded assets
- `--disable-youtube` - Disable YouTube asset fetching
- `--disable-pexels` - Disable Pexels asset fetching

### Examples

```powershell
# Basic usage
python -m vid_orchestrator script.md --output timeline.fcpxml

# With Pexels and verbose logging
python -m vid_orchestrator script.md -o timeline.fcpxml --pexels-key YOUR_KEY -v

# Resolve integration
python -m vid_orchestrator script.md -o timeline.fcpxml --resolve

# Test script parsing without fetching assets
python -m vid_orchestrator script.md -o test.fcpxml --no-fetch

# YouTube only (no Pexels)
python -m vid_orchestrator script.md -o timeline.fcpxml --disable-pexels
```

## Configuration

### Environment Variables

- `PEXELS_API_KEY` - Your Pexels API key for stock footage access

### Getting API Keys

**Pexels API Key:**
1. Visit https://www.pexels.com/api/
2. Sign up for a free account
3. Generate an API key
4. Set it as an environment variable or pass via `--pexels-key`

## Output Format

### FCPXML 1.8 Structure

The generated FCPXML contains:

- **Format Resource** - 1920x1080 @ 30fps
- **Media Resources** - References to downloaded B-roll files
- **Spine Track** - Gaps representing voiceover segments (5-10s each)
- **Lane 1** - Connected clips with B-roll footage aligned to spine

### Timeline Organization

```
Spine (Voiceover):  [Gap 1][Gap 2][Gap 3][Gap 4]...
Lane 1 (B-roll):    [Clip 1][Clip 2][Clip 3][Clip 4]...
```

Each gap/clip pair represents one beat from your script.

## Testing

Run the test suite:

```powershell
python run_tests.py
```

Or using unittest:

```powershell
python -m unittest tests.test_end_to_end_integration -v
```

See `tests/README.md` for detailed test documentation.

## Project Structure

```
footage/
├── vid_orchestrator/              # Main package
│   ├── __init__.py               # Package initialization
│   ├── __main__.py               # Module entry point
│   ├── cli.py                    # CLI interface
│   ├── orchestrator.py           # Main workflow coordinator
│   ├── resolve_integration.py    # DaVinci Resolve integration
│   ├── core/
│   │   └── beat.py              # Beat dataclass
│   ├── parsing/
│   │   └── script_parser.py     # Markdown parser
│   ├── fetchers/
│   │   ├── base_fetcher.py      # Abstract fetcher interface
│   │   ├── asset_orchestrator.py # Fetcher coordinator
│   │   ├── youtube_client.py    # YouTube downloader
│   │   └── pexels_client.py     # Pexels API client
│   ├── generators/
│   │   └── xml_generator.py     # FCPXML generator
│   └── utils/
│       └── error_handling.py    # Error handling utilities
├── tests/                        # Test suite
│   ├── test_end_to_end_integration.py
│   ├── fixtures/
│   │   └── sample_script.md
│   └── README.md
├── docs/
│   └── MARKDOWN_SCRIPT_GUIDE.md # Writing guide
├── vid_orchestrator_cli.py      # Standalone CLI script
├── run_tests.py                 # Test runner
└── README.md                    # This file
```

## Troubleshooting

### Common Issues

**"yt-dlp not installed"**
```powershell
pip install --upgrade yt-dlp
```

**"ffmpeg not found"**
- Install ffmpeg and ensure it's in your PATH
- Windows: `choco install ffmpeg` or download from ffmpeg.org

**"No beats were generated"**
- Check that your script has sufficient content (minimum 13 words for one beat)
- Verify markdown file is not empty

**"Pexels API authentication failed"**
- Verify your API key is correct
- Check that the key hasn't exceeded rate limits

**"Beats are too short/long"**
- Aim for 13-25 words per paragraph
- Use the markdown script guide for optimal formatting

### Debugging

Enable verbose logging to see detailed information:

```powershell
python -m vid_orchestrator script.md --output timeline.fcpxml --verbose
```

## Contributing

Contributions are welcome! Areas for improvement:

- Additional asset fetchers (e.g., Pixabay, Shutterstock)
- More sophisticated beat timing algorithms
- Better search query generation using NLP
- Support for multiple voice-over tracks
- Timeline preview/validation tools

## License

[Add your license information here]

## Acknowledgments

- Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube downloads
- [Pexels API](https://www.pexels.com/api/) for stock footage
- [ffmpeg](https://ffmpeg.org/) for video processing
- FCPXML 1.8 specification for timeline format

---

# Markdown Script Specification

## Overview

This specification defines the markdown script format used by vid-orchestrator to generate video timelines with automatic B-roll placement.

## Format Version

**Version:** 1.0  
**Compatible with:** vid-orchestrator 0.1.0+

## Design Principles

1. **Natural Language First** - Scripts should read like natural speech
2. **Visual Keywords** - Include concrete, visual elements for B-roll generation
3. **Timing-Based Chunking** - Text is automatically segmented based on speaking duration
4. **Context-Aware** - Headers provide context for search query generation

## File Format

### Extension
- `.md` (markdown)
- `.markdown`
- `.txt` (accepted but not recommended)

### Encoding
- UTF-8 (preferred)
- Fallback: latin-1, cp1252, iso-8859-1

## Structure Elements

### 1. Headers

Headers provide contextual information that influences B-roll search query generation.

#### Level 1 Header (`#`)
- Represents the main topic/title
- Provides high-level context for all beats
- One per document recommended

**Example:**
```markdown
# Python Programming Tutorial
```

#### Level 2 Header (`##`)
- Represents section topics
- Provides context for beats within that section
- Multiple per document

**Example:**
```markdown
## Setting Up Your Environment
## Writing Your First Program
```

#### Level 3+ Headers
- Currently treated as regular text
- Not used for contextual hierarchy

### 2. Body Text

Body text is automatically parsed and chunked into beats (5-10 second segments).

#### Paragraph Structure
- Continuous text blocks are parsed as single units
- Blank lines separate paragraphs but don't affect beat generation
- Sentences are split on `.`, `!`, `?` for natural chunking boundaries

#### Word Count Guidelines

Based on **2.5 words per second** heuristic:

| Word Count | Duration | Beat Status |
|------------|----------|-------------|
| < 13 words | < 5 seconds | Too short - will be merged |
| 13-25 words | 5-10 seconds | **Optimal** |
| > 25 words | > 10 seconds | Too long - will be split |

**Example:**
```markdown
First, you need to install Python on your computer. Visit the official Python website and download the latest version for your operating system.
```

This becomes **2 beats**:
- Beat 1: "First, you need to install Python on your computer." (~10 words, 4s)
- Beat 2: "Visit the official Python website and download the latest version for your operating system." (~15 words, 6s)

### 3. Ignored Elements

The following markdown elements are **ignored** or stripped:

- Code blocks (` ``` `)
- Inline code (`` ` ``)
- Links (converted to text only)
- Images
- Tables
- Lists (converted to plain text)
- Bold/italic formatting
- Blockquotes

## Beat Generation Algorithm

### Step 1: Extract Content
1. Parse markdown file
2. Extract headers → context
3. Extract body text → content to chunk

### Step 2: Text Chunking
1. Split text into sentences (`.`, `!`, `?`)
2. Group sentences to target 13-25 words
3. Ensure minimum 13 words per beat
4. Split beats exceeding 25 words

### Step 3: Beat Creation
For each text chunk:
1. **Generate Beat ID**: `beat_001`, `beat_002`, etc.
2. **Calculate Duration**: `word_count / 2.5` seconds
3. **Generate Stock Keyword**: Extract visual nouns from text + context
4. **Generate YouTube Phrase**: Extract technical terms + actions from text + context
5. **Create Beat Object**: With all metadata

### Step 4: Validation
- Verify each beat is 5-10 seconds
- Ensure search queries are non-empty
- Check text content is valid

## Search Query Generation

### Stock Keywords (for Pexels)

**Purpose:** Find generic stock footage

**Algorithm:**
1. Extract nouns and action verbs from beat text
2. Filter stop words ("the", "a", "is", etc.)
3. Prioritize visual keywords:
   - Software names: "Visual Studio Code", "Chrome"
   - Actions: "typing", "clicking", "programming"
   - Objects: "keyboard", "computer", "screen"
4. Include context from headers
5. Return top 3 keywords

**Example:**
- Text: "Open Visual Studio Code and create a new Python file"
- Context: "Python Programming Tutorial"
- Stock Keyword: `"code editor programming"`

### YouTube Search Phrases

**Purpose:** Find specific tutorial/demo content

**Algorithm:**
1. Extract technical terms and product names
2. Extract meaningful verbs (>3 letters)
3. Include context from headers
4. Prioritize specific over generic terms
5. Return top 4 terms as phrase

**Example:**
- Text: "Navigate to the terminal window and type the python command"
- Context: "Setting Up Python"
- YouTube Phrase: `"terminal python command setup"`

## Best Practices

### ✅ DO

1. **Use descriptive headers**
   ```markdown
   ## Installing Python on Windows
   ```

2. **Include specific tool/software names**
   ```markdown
   Open Visual Studio Code and click the Extensions icon.
   ```

3. **Mention visual elements**
   ```markdown
   In the blue sidebar, locate the gear icon.
   ```

4. **Write in active voice**
   ```markdown
   Click the green Run button to execute your code.
   ```

5. **Target 13-25 words per intended beat**
   ```markdown
   First, download the installer from the official website. Then run the setup wizard and follow the on-screen instructions.
   ```

### ❌ DON'T

1. **Use overly abstract language**
   ```markdown
   ❌ Consider the philosophical implications of software design.
   ✅ Open the code editor and create a new project folder.
   ```

2. **Write very long paragraphs**
   ```markdown
   ❌ (50+ word paragraph)
   ✅ Break into 2-3 shorter sentences
   ```

3. **Use only pronouns without context**
   ```markdown
   ❌ Click on it and select that option.
   ✅ Click on the File menu and select New Project.
   ```

4. **Include code blocks in voiceover text**
   ```markdown
   ❌ Type the following: `print("Hello")`
   ✅ Type print with the message "Hello" in parentheses.
   ```

## Example Scripts

### Example 1: Tutorial Format

```markdown
# Getting Started with Python

## Introduction
Welcome to this Python programming tutorial. In this video, we'll cover the basics of Python development and create your first program.

## Installing Python
First, visit the official Python website at python.org and download the latest version. The installation process is straightforward and takes just a few minutes to complete.

## Your First Program
Open your text editor and create a new file called hello.py. Type the print function with your message inside quotes.

## Running Your Code
Open the terminal or command prompt and navigate to your file location. Type python followed by your filename to execute the program.
```

**Generated Beats:** ~4-5 beats with durations between 5-10 seconds

### Example 2: Product Demo Format

```markdown
# Video Editor Demo: Basic Editing

## Opening Your Project
Launch the video editor from your applications folder. Click the New Project button and choose your project settings.

## Importing Media
Navigate to the File menu and select Import Media. Choose your video clips from the file browser and click Open.

## Timeline Editing
Drag your clips onto the timeline at the bottom of the screen. Use the razor tool to split clips and the selection tool to rearrange them.

## Adding Transitions
Click on the Transitions panel in the left sidebar. Drag a crossfade transition between two clips to create a smooth transition effect.

## Exporting Your Video
When you're finished editing, click the Export button in the top toolbar. Choose your export format and click the Start Export button.
```

**Generated Beats:** ~5-6 beats with specific actions and UI references

## Validation Rules

A valid markdown script must:

1. **File Requirements**
   - File must exist and be readable
   - File size > 0 bytes
   - File size < 10MB (warning for larger files)

2. **Content Requirements**
   - Must contain at least 13 words total
   - Must produce at least 1 valid beat (13-25 words)
   - Text content after stripping whitespace

3. **Beat Requirements**
   - Each beat must be 5-10 seconds (13-25 words)
   - Each beat must have non-empty stock_keyword
   - Each beat must have non-empty youtube_search_phrase
   - Beat text cannot be empty

## Error Handling

### Warnings
- No markdown headers found
- File encoding is not UTF-8
- Script is very short (<5s estimated)
- Script is very long (>10 minutes estimated)

### Errors
- File not found
- File is empty
- Cannot decode file (unsupported encoding)
- No valid beats generated
- Beat validation fails (duration out of range)

## Testing Your Scripts

### Dry Run (No Asset Fetching)
```powershell
python -m vid_orchestrator script.md --output test.fcpxml --no-fetch --verbose
```

This shows:
- How many beats are generated
- Duration of each beat
- Search queries for each beat
- FCPXML structure

### Validation Checklist
- [ ] Each paragraph is 13-25 words
- [ ] Specific software/tool names mentioned
- [ ] Visual elements described (buttons, menus, windows)
- [ ] Actions clearly stated (click, type, open, select)
- [ ] Headers provide clear section context
- [ ] Script reads naturally when spoken aloud

## Version History

**v1.0** (Initial Release)
- Markdown parsing with header extraction
- 2.5 words/second timing heuristic
- 5-10 second beat constraints
- Auto-generated stock keywords and YouTube phrases
- UTF-8 with encoding fallback support
