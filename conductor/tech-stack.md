# Tech Stack: vid-orchestrator

## Core Language & Runtime
- **Python 3.7+:** The primary language for orchestration, parsing, and CLI logic.

## Media Processing & External Tools
- **ffmpeg:** Essential for video trimming, transcoding, and duration verification.
- **yt-dlp:** Used for searching and downloading video assets from YouTube.

## APIs & Integration
- **Pexels API:** Primary source for high-quality stock footage assets.
- **FCPXML 1.8:** Industry-standard XML format used to export timelines for DaVinci Resolve and Final Cut Pro.

## Libraries & Frameworks
- **argparse:** Standard Python library for robust command-line argument parsing.
- **requests:** For making HTTP requests to the Pexels API.
- **xml.etree.ElementTree:** For generating and manipulating FCPXML documents.

## Quality Assurance
- **unittest:** Standard Python testing framework for unit and integration tests.
- **flake8/pylint:** (Detected) For maintaining code quality and PEP 8 compliance.
