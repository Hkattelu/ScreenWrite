# Footage Web App

A modern web interface for the **vid-orchestrator** CLI tool. Convert markdown video scripts into DaVinci Resolve-compatible timelines with automatic B-roll fetching, all through an intuitive web UI.

## Features

- **📝 Upload & Parse**: Upload markdown scripts and automatically parse into beat segments
- **🎬 Visual Preview**: See parsed beats with durations, keywords, and search queries
- **⚙️ Configure Fetching**: Choose YouTube and/or Pexels as asset sources
- **📥 Auto B-roll**: Automatically fetch footage based on your script descriptions
- **🎯 Smart Fallback**: Seamlessly switch between YouTube and Pexels when content unavailable
- **⚡ Generate Timeline**: Create FCPXML files ready for DaVinci Resolve import
- **📊 Real-time Progress**: Track asset downloading with live progress updates

## Project Structure

```
webapp/
├── backend/                    # Flask REST API
│   ├── routes/                # API endpoint handlers
│   │   ├── upload.py          # File upload & parsing
│   │   ├── api.py             # Session management
│   │   └── export.py          # FCPXML generation
│   ├── app.py                 # Flask application
│   └── requirements.txt        # Python dependencies
├── frontend/                   # React + Vite UI
│   ├── src/
│   │   ├── components/        # Reusable React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API client
│   │   ├── types/             # TypeScript definitions
│   │   └── styles/            # CSS & Tailwind
│   ├── package.json
│   └── vite.config.ts
└── README.md                   # This file
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
cd webapp/backend

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate      # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional)
cp .env.example .env

# Run Flask server
python app.py
# Server runs on http://localhost:5000
```

### Frontend Setup

```bash
cd webapp/frontend

# Install dependencies
npm install

# Start development server
npm run dev
# App runs on http://localhost:3000
```

The frontend is configured to proxy API requests to the backend, so you can develop without CORS issues.

## Usage

1. **Visit the web app**: Open http://localhost:3000 in your browser
2. **Upload a script**: Select or drag-drop a markdown file
3. **Review beats**: Check auto-parsed beats and edit if needed
4. **Configure**: Choose YouTube/Pexels sources and add API keys (if using Pexels)
5. **Export**: Generate FCPXML timeline
6. **Download**: Get your FCPXML file ready for DaVinci Resolve

## Script Format

Your markdown script should follow this pattern:

```markdown
## Introduction
This is the opening. We need footage of
a sunrise with a peaceful vibe.

## Main Section
Show office workers collaborating.
Quick cuts of teamwork in action.

## Conclusion  
End with an inspiring sunset shot.
```

Each section:
- Starts with a header (##)
- Contains a description of the footage needed
- Duration is auto-calculated from text length
- Stock keywords and YouTube phrases are generated automatically

## API Endpoints

### Upload & Parse
```
POST /api/upload
Content-Type: multipart/form-data
Body: { file: File }

Response:
{
  sessionId: string,
  beats: Beat[],
  summary: {
    totalBeats: number,
    estimatedDuration: number,
    warnings: string[]
  }
}
```

### Session Management
```
GET /api/session/:sessionId
GET /api/session/:sessionId/status
PUT /api/session/:sessionId/config
PUT /api/session/:sessionId/beats
DELETE /api/session/:sessionId/delete
```

### Export
```
POST /api/session/:sessionId/export
Body: { filename?: string, resolveIntegration?: boolean }

Response:
{
  fcpxmlPath: string,
  downloadUrl: string,
  assetCount: number,
  beatCount: number,
  estimatedDuration: number
}
```

## Configuration

### Backend (.env)
```
FLASK_ENV=development          # development or production
FLASK_PORT=5000                # Server port
UPLOAD_FOLDER=./uploads         # Temp upload location
SESSION_FOLDER=./sessions       # Session data storage
```

### Frontend (vite.config.ts)
```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:5000',  // Backend URL
      changeOrigin: true,
    },
  },
}
```

## Development

### Building
```bash
# Frontend
cd webapp/frontend
npm run build  # Produces dist/ directory

# Backend
# No build step required - runs directly with Python
```

### Testing
```bash
# Backend tests (when added)
cd webapp/backend
python -m pytest tests/

# Frontend tests (when added)
cd webapp/frontend
npm run test
```

### Linting
```bash
# Frontend
cd webapp/frontend
npm run lint

# Backend (if configured)
cd webapp/backend
flake8 . 
pylint .
```

## Deployment

### Production Build
```bash
# Build frontend
cd webapp/frontend
npm run build

# This creates an optimized `dist/` directory

# Backend: Use production-grade WSGI server
pip install gunicorn
gunicorn app:app --workers 4 --bind 0.0.0.0:5000
```

### Docker (Optional)
Create a `Dockerfile` in the webapp directory to containerize the entire application.

## Known Limitations

- File upload size limited to 16MB
- Asset download timeout: 60 seconds per beat
- YouTube/Pexels API rate limits apply
- FCPXML generation requires all beats to have parsed data

## Troubleshooting

### "Failed to upload file"
- Check file is markdown (.md) or text (.txt)
- Ensure file size < 16MB
- Verify backend is running (http://localhost:5000/api/health)

### "No beats generated from script"
- Check markdown formatting (headers must use ##)
- Ensure sections have descriptive text
- Avoid empty sections

### "Pexels API errors"
- Verify API key is correct (if using paid tier)
- Check API key has appropriate permissions
- Pexels free tier has rate limits

### "DaVinci Resolve won't import FCPXML"
- Verify Resolve version supports FCPXML 1.8
- Check that asset paths are correct and accessible
- Try generating with a simpler script first

## Environment Variables

### Backend Required
- None (defaults work fine for development)

### Backend Optional
- `FLASK_ENV`: Set to `production` for production use
- `FLASK_PORT`: Custom port (default: 5000)
- `UPLOAD_FOLDER`: Custom upload directory (default: ./uploads)
- `SESSION_FOLDER`: Custom session directory (default: ./sessions)

### Frontend
- All configuration is in `vite.config.ts`
- Update the proxy target if backend is on a different host/port

## Contributing

This is part of the **footage** project. See the main [README.md](../README.md) for contribution guidelines.

## License

MIT License - See LICENSE file

## Support

For issues and questions:
- Check the [main README](../README.md)
- Review the [troubleshooting guide](./docs/TROUBLESHOOTING.md) (when created)
- Open an issue on GitHub

## Roadmap

Future enhancements planned:
- [ ] Real-time progress streaming (SSE/WebSocket)
- [ ] Asset gallery with video previews
- [ ] Project persistence and loading
- [ ] Batch script processing
- [ ] Custom beat templates
- [ ] Direct Resolve integration (optional)
- [ ] Asset caching and reuse
- [ ] Analytics and usage tracking
