# ScreenWrite Web UI

A modern web interface for the **ScreenWrite** engine. Convert markdown scripts into DaVinci Resolve timelines with automatic B-roll fetching through an intuitive, editorial-style interface.

## Features

- **📝 Upload & Parse**: Instantly convert markdown into timed video beats.
- **🎬 Visual Review**: Fine-tune your script and visual search queries.
- **⚙️ Source Control**: Choose between YouTube, Pexels, or intentional empty gaps.
- **⚡ Pro Export**: Generate and download FCPXML 1.8 files.

---

## Quick Start

### 1. Backend Setup (Flask)
```bash
cd webapp/backend
python -m venv venv
source venv/Scripts/activate # Windows
pip install -r requirements.txt
python app.py
```

### 2. Frontend Setup (React)
```bash
cd webapp/frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to begin.

---

## Project Structure

```
webapp/
├── backend/          # Flask REST API
│   ├── routes/       # API endpoints (Upload, Session, Export)
│   └── app.py        # Entry point
├── frontend/         # React + Vite (TypeScript)
│   ├── src/          # Components, Pages, and Services
│   └── package.json  # Dependencies
└── README.md         # This file
```

---

## Configuration

The Web UI uses the same core engine as the CLI. Set your `PEXELS_API_KEY` in your environment to enable stock footage fallback.

For deployment configuration, see the `.env.example` file in the backend directory.