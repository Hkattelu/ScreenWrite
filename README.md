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
If you are on **Windows**, run:
```powershell
./setup.ps1
```

If you are on **macOS** or **Linux**, run:
```bash
chmod +x setup.sh && ./setup.sh
```

### The Manual Way

**1. Backend Setup:**
```bash
cd webapp/backend
python -m venv venv
./venv/Scripts/activate # or source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**2. Frontend Setup:**
```bash
cd webapp/frontend
npm install
npm run dev
```

Visit `http://localhost:3000`. 
**💡 Pro Tip:** Don't have a script ready? Click **"Try with an Example"** on the upload screen to see ScreenWrite in action immediately.

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