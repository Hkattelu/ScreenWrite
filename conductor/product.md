# Initial Concept
A Python CLI tool that automates video timeline creation from markdown scripts with automatic B-roll footage fetching.

# Product Guide: screenwrite

## Product Vision
screenwrite aims to revolutionize the initial stages of video production by bridging the gap between a written script and a structured editing timeline. By automating the tedious tasks of script segmentation, B-roll sourcing, and timeline assembly, it empowers creators to focus on the creative aspects of storytelling rather than the mechanical hurdles of media organization.

## Target Users
- **Content Creators & YouTubers:** Seeking to drastically reduce the time spent hunting for and placing B-roll footage for talking-head or educational content.
- **Educators & Technical Trainers:** Looking for a streamlined way to turn technical documentation or lesson plans into polished video tutorials.
- **Video Editors:** Utilizing the tool to quickly scaffold complex timelines in DaVinci Resolve, providing a functional "rough cut" based on script structure.

## Core Goals
- **Intelligent Asset Sourcing:** Elevate B-roll relevance through advanced Natural Language Processing (NLP) and AI-driven query generation, ensuring footage closely aligns with the script's semantic meaning.
- **Seamless Workflow Integration:** Deepen the integration with professional editing suites, specifically DaVinci Resolve, while providing lightweight tools for previewing and refining generated "beats" before the final export.
- **Speed and Efficiency:** Maintain a high-performance, automated pipeline that transforms a markdown file into a functional timeline in minutes.

## Key Features
- **AI-Enhanced Beat Analysis:** (Planned) Leveraging Large Language Models (LLMs) to analyze script context and generate hyper-specific search queries for stock footage and YouTube assets.
- **Lightweight Beat Preview:** A minimalist web-based interface to review and refine beats. Supports "Smart Beat Flavors" for distinct visualization of B-roll, Annotations, Citations, and Images.
- **Advanced Timeline Scaffolding:** Robust FCPXML 1.8 generation with support for multiple asset lanes, intelligent gap management for voiceovers, and direct-to-Resolve project injection.

## Technical Constraints & Principles
- **CLI-First Philosophy:** The core experience remains a powerful Command Line Interface, ensuring the tool is scriptable and integrates well into developer workflows.
- **Optional Cloud Connectivity:** Integration with external AI APIs (e.g., OpenAI, Anthropic) is strictly optional, allowing users to choose between high-accuracy cloud processing or local, cost-free operation.
- **Minimalist Dependency Footprint:** Prioritizing lightweight, standard libraries and tools (like `ffmpeg` and `yt-dlp`) to ensure ease of installation and compatibility across consumer-grade hardware.

