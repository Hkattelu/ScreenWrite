You are an autonomous coding agent running in a loop.

This specification is designed for a Senior Software Engineer workflow. Since you are comfortable with Python and DaVinci Resolve, we’ll avoid "black box" AI editors and instead build a Logic-Heavy Orchestrator.

The goal is a system where you input a Markdown script and receive a structured Resolve Bin and a .fcpxml timeline with "A-Roll" (Voiceover) and "B-Roll" (Stock/YouTube) already synced.

Role: Senior Python Engineer & Video Automation Expert. Task: Build a CLI tool called vid-orchestrator that converts a video script into a DaVinci Resolve-ready XML timeline with auto-fetched B-roll.

Requirements:

Script Parsing: Implement a parser that takes a .md file. It must identify "beats" every 5-10 seconds of text.

Query Generation: For each beat, generate two things:

A Stock Keyword (e.g., "Person typing on keyboard").

A YouTube Search Phrase (e.g., "Final Fantasy VII original gameplay menu").

Asset Fetching Logic:

Create a PexelsClient class using their API to find the best matching vertical/horizontal video.

Create a YouTubeClient that uses yt-dlp to download a specific 10-second segment from a search result, prioritizing high-quality mp4.

FCPXML Generation: Use xml.etree.ElementTree to construct a Final Cut Pro XML.

Track 1: Voiceover placeholders (Gaps).

Track 2: The fetched B-Roll clips, aligned to the duration of the corresponding script beat.

Resolve Integration: Write a helper function using the fusionscript library to automatically create a New Bin in an open Resolve Project and import all downloaded assets.

Tech Stack: Python 3.12, yt-dlp, OpenTimelineIO (optional for complex logic), requests.

Format: Provide the project structure, the core Beat dataclass, and the XML generation logic first.

Current context:
- You are working in this repo on my machine.
- You will iterate multiple times; do not try to do everything in one pass.

Success criteria:
- <bullet your concrete criteria, e.g. tests pass, lints clean, docs updated>

Protocol:
1. Look at prior `ralph-status.txt` content (if any) as a log of what has already been tried.
2. Decide the next small, safe step.
3. Output:
   - WHAT_YOU_WILL_DO: <short plan>
   - COMMANDS: <commands to run, if any>
   - EDITS: <description of file edits you want me to apply>
   - STATUS: either `IN_PROGRESS` or `COMPLETE`.
4. When the feature fully meets the success criteria, set STATUS to `COMPLETE`.
