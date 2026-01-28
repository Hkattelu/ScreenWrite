# 🎬 ScreenWrite

**Script to Timeline, Automatically.**

ScreenWrite is an automated video production engine that transforms Markdown scripts into professionally structured DaVinci Resolve timelines. It parses your script, generates intelligent B-roll search queries, and fetches high-quality assets from YouTube and Pexels—all in one workflow.

---

## ✨ Features

- **📝 Editorial Markdown Parser**: Converts standard markdown into timed video "beats" (5-10s segments).
- **🎬 Automated B-roll**: Intelligently fetches footage from YouTube (yt-dlp) and Pexels Stock.
- **⚡ Pro-Grade Export**: Generates FCPXML 1.8 files ready for direct import into DaVinci Resolve or Final Cut Pro.
- **🖥️ Minimalist Web UI**: A clean, "editorial-style" web interface for reviewing and fine-tuning your timeline.
- **🛠️ Powerful CLI**: Robust command-line tool for automated batch processing.
- **🎯 Smart Fallback**: Prioritizes specific YouTube clips with seamless fallback to Pexels stock footage.

---

## 🚀 Quick Start (GitHub)

### The One-Command Way
Get up and running in seconds. This script will set up your virtual environment, install all dependencies, and guide you through the initial configuration (including your Gemini API key).

**On Windows:**
```powershell
./setup.ps1
```

**On macOS / Linux:**
```bash
chmod +x setup.sh && ./setup.sh
```

The script will:
1. Verify **Python 3.7+** and **Node.js** are installed.
2. Check for system dependencies (**ffmpeg**, **yt-dlp**).
3. Create a local virtual environment and install requirements.
4. Prompt you for your **Gemini API Key** to enable AI features.

---

## 📖 The Script Format

ScreenWrite uses a refined Markdown syntax designed for video creators.

```markdown
Title: My Documentary
Hook: A journey through the clouds.

## Introduction
The sun rises over the distant peaks, 
casting long shadows across the valley.

[@B-roll: aerial view of mountains at sunrise]
Nature has a way of reminding us 
of our place in the world.
```

- **Headers (`##`)**: Define new sections and provide search context.
- **Paragraphs**: Automatically chunked into 5-10 second segments.
- **Instructions (`[@...]`)**: Explicitly request specific B-roll or Annotations.

---

## 🛠️ Architecture

ScreenWrite is built on a modular pipeline designed for extensibility:

1.  **Parser**: Text → Timing → Search Queries
2.  **Orchestrator**: Coordinates multi-source asset fetching.
3.  **Fetchers**: YouTube (yt-dlp) & Pexels (API) integrations.
4.  **Generator**: Produces standard FCPXML 1.8 manifests.

---

## ⚙️ Configuration

Set your Pexels API key to enable high-quality stock footage:

```bash
# Windows (PowerShell)
$env:PEXELS_API_KEY = "your_key_here"

# Linux / macOS
export PEXELS_API_KEY="your_key_here"
```

---

## ⚖️ License

MIT License. See `LICENSE` for details.