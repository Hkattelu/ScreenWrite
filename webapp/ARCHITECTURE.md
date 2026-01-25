# Web App Architecture

Detailed architecture documentation for the footage web app.

## System Overview

The web app is a modern full-stack application that wraps the existing `vid_orchestrator` CLI tool in an intuitive web interface.

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Browser                            │
│                 (http://localhost:3000)                      │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP + JSON
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Frontend (React + Vite)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Pages: Home, Workflow                                  │ │
│  │ Components: Upload, BeatList, ConfigPanel             │ │
│  │ Services: API client with axios                        │ │
│  │ Styling: Tailwind CSS                                 │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────────┘
                   │ REST API calls
                   │ /api/upload, /api/session/*, /api/export
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend (Flask + Python)                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Routes:                                                │ │
│  │  - upload.py: Parse scripts into beats               │ │
│  │  - api.py: Session management                         │ │
│  │  - export.py: FCPXML generation                       │ │
│  │                                                        │ │
│  │ Services:                                             │ │
│  │  - Session state (JSON files)                         │ │
│  │  - Configuration management                           │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────────┘
                   │ Python imports
                   ▼
┌─────────────────────────────────────────────────────────────┐
│         vid_orchestrator (Existing CLI)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ - ScriptParser: markdown → beats                      │ │
│  │ - XMLGenerator: beats → FCPXML                        │ │
│  │ - Beat dataclass: core data structure                 │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  File System    │
         │  sessions/      │
         │  uploads/       │
         │  output/        │
         └─────────────────┘
```

## Component Hierarchy

### Frontend Components

```
App.tsx
├── Router (React Router)
│
├── Home page
│   ├── Hero section
│   ├── Features grid
│   ├── Workflow steps
│   └── Script format guide
│
└── Workflow page
    ├── Step indicator (1. Upload, 2. Review, 3. Configure, 4. Export)
    │
    ├── Step 1: Upload
    │   └── ScriptUpload component
    │       ├── Drag-drop zone
    │       ├── File input
    │       └── Error display
    │
    ├── Step 2: Review
    │   └── BeatList component
    │       ├── Summary stats
    │       ├── Beat display
    │       └── Edit mode (inline)
    │
    ├── Step 3: Configure
    │   └── ConfigPanel component
    │       ├── YouTube toggle
    │       ├── Pexels configuration
    │       └── Output directory
    │
    └── Step 4: Export
        ├── Export confirmation
        ├── File download
        └── Success message
```

## Data Flow

### Upload → Parse Flow

```
User clicks "Choose File"
    │
    ▼
ScriptUpload component
    │
    ├─ Validate file type (.md or .txt)
    ├─ Show loading state
    │
    ▼
uploadScript() API call
    │
    POST /api/upload
    │
    ▼
Backend: upload.py
    │
    ├─ Save file to uploads/ folder
    ├─ Create session directory
    ├─ Import ScriptParser
    │
    ▼
ScriptParser.parse_file()
    │
    ├─ Read markdown
    ├─ Extract sections (by ##)
    ├─ Calculate duration per section
    ├─ Generate stock keywords
    ├─ Generate YouTube search phrases
    │
    ▼
Return Beat[] objects
    │
    ▼
Backend constructs JSON response
    │
    {
      sessionId: "uuid-here",
      beats: [{id, text, duration, stock_keyword, youtube_phrase}, ...],
      summary: {totalBeats, estimatedDuration, warnings}
    }
    │
    ▼
Frontend receives response
    │
    ├─ Extract sessionId (save for later)
    ├─ Store beats in component state
    └─ Navigate to review step
```

### Session State Management

```
Backend maintains session JSON structure:

sessions/
├── {sessionId}/
│   ├── state.json  (Session state file)
│   ├── {filename}  (Uploaded script)
│   ├── timeline.fcpxml  (Generated output)
│   └── ...other files

state.json structure:
{
  "sessionId": "uuid",
  "status": "upload|configured|exported",
  "config": {
    "youtube_enabled": true,
    "pexels_enabled": true,
    "pexels_api_key": "...",
    "output_dir": "./output"
  },
  "beats": [{Beat objects}],
  "assets": [{Asset objects}],
  "createdAt": "2026-01-25T...",
  "updatedAt": "2026-01-25T..."
}
```

### Export Flow

```
User clicks "Generate Timeline"
    │
    ▼
Workflow component calls exportFcpxml()
    │
    POST /api/session/{id}/export
    │
    ▼
Backend: export.py
    │
    ├─ Load session state
    ├─ Reconstruct Beat objects from state
    ├─ Retrieve assets (if available)
    │
    ▼
XMLGenerator.generate(beats, assets, output_path)
    │
    ├─ Create FCPXML document structure
    ├─ Set format (1920x1080, 30fps)
    ├─ Create media resources
    ├─ Build timeline spine with gaps
    ├─ Add B-roll clips to connected lane
    │
    ▼
Write timeline.fcpxml to disk
    │
    ▼
Return export info to frontend
    │
    {
      fcpxmlPath: "...",
      downloadUrl: "/api/session/{id}/download/timeline.fcpxml",
      assetCount: 5,
      beatCount: 3,
      estimatedDuration: 42.5
    }
    │
    ▼
Frontend displays download link
    │
    User clicks to download FCPXML
```

## API Contract Specification

### POST /api/upload

**Purpose**: Upload markdown script and parse into beats

**Request**:
```
Content-Type: multipart/form-data
Body: {
  file: File (markdown or text)
}
```

**Response** (200 OK):
```json
{
  "sessionId": "123e4567-e89b-12d3-a456-426614174000",
  "beats": [
    {
      "id": "beat-uuid",
      "text": "Beat description text",
      "duration": 5.2,
      "stock_keyword": "sunrise mountains",
      "youtube_phrase": "beautiful sunrise over mountains",
      "header": "Introduction"
    }
  ],
  "summary": {
    "totalBeats": 3,
    "estimatedDuration": 15.6,
    "warnings": []
  }
}
```

**Errors**:
- `400` - No file, wrong type, or parsing failed
- `500` - Server error

### PUT /api/session/{sessionId}/config

**Purpose**: Update session configuration

**Request**:
```json
{
  "youtubeEnabled": true,
  "pexelsEnabled": true,
  "pexelsApiKey": "optional-key",
  "outputDir": "./output"
}
```

**Response** (200 OK):
```json
{ "success": true }
```

### PUT /api/session/{sessionId}/beats

**Purpose**: Update beats (after editing)

**Request**:
```json
{
  "beats": [
    {
      "id": "beat-uuid",
      "text": "edited text",
      "duration": 6.0,
      "stock_keyword": "edited-keyword",
      "youtube_phrase": "edited phrase"
    }
  ]
}
```

**Response** (200 OK):
```json
{ "success": true }
```

### POST /api/session/{sessionId}/export

**Purpose**: Generate FCPXML file

**Request**:
```json
{
  "filename": "timeline.fcpxml",
  "resolveIntegration": false
}
```

**Response** (200 OK):
```json
{
  "sessionId": "uuid",
  "fcpxmlPath": "/absolute/path/timeline.fcpxml",
  "downloadUrl": "/api/session/{id}/download/timeline.fcpxml",
  "filename": "timeline.fcpxml",
  "assetCount": 5,
  "beatCount": 3,
  "estimatedDuration": 42.5,
  "fileSize": 12345,
  "generatedAt": "2026-01-25T10:30:00"
}
```

### GET /api/session/{sessionId}/download/{filename}

**Purpose**: Download file from session

**Response**: File (binary download)

**Security**: Only allows downloading files from within the session directory

## Type System (TypeScript)

### Core Types

```typescript
// Main beat structure
interface Beat {
  id: string
  text: string
  duration: number
  stock_keyword: string
  youtube_phrase: string
  header?: string
}

// Session workflow state
interface SessionState {
  sessionId: string
  status: 'initialized' | 'configured' | 'fetching' | 'complete' | 'error'
  config: Config
  beats: Beat[]
  assets: Asset[]
}

// User-facing configuration
interface Config {
  youtubeEnabled: boolean
  pexelsEnabled: boolean
  pexelsApiKey?: string
  outputDir?: string
}

// Downloaded/available assets
interface Asset {
  id: string
  beatId: string
  source: 'youtube' | 'pexels'
  title: string
  thumbnail?: string
  url: string
  duration: number
  fileSize?: number
  status: 'pending' | 'downloading' | 'success' | 'failed'
}
```

## File Organization

### Backend (Python)

```
webapp/backend/
├── app.py                  # Main Flask app (70 lines)
│                           # - Flask initialization
│                           # - CORS setup
│                           # - Error handlers
│                           # - Health check endpoint
│
├── routes/
│   ├── __init__.py
│   ├── upload.py           # Upload endpoint (120 lines)
│   │                       # - File validation
│   │                       # - ScriptParser integration
│   │                       # - Session creation
│   │
│   ├── api.py              # Session routes (150 lines)
│   │                       # - Get/update session
│   │                       # - Config management
│   │                       # - Status queries
│   │
│   └── export.py           # Export routes (130 lines)
│                           # - FCPXML generation
│                           # - File download
│
├── requirements.txt        # Python dependencies
└── .env.example            # Environment template
```

### Frontend (TypeScript/React)

```
webapp/frontend/src/
├── App.tsx                 # Main app component (20 lines)
├── main.tsx                # React DOM render entry
│
├── pages/
│   ├── Home.tsx            # Home page (130 lines)
│   │                       # - Welcome screen
│   │                       # - Features overview
│   │                       # - Workflow steps
│   │
│   └── Workflow.tsx        # Multi-step wizard (200 lines)
│                           # - Step management
│                           # - Upload → Review → Configure → Export
│
├── components/
│   ├── ScriptUpload.tsx    # Upload component (100 lines)
│   │                       # - Drag-drop zone
│   │                       # - File validation
│   │
│   ├── BeatList.tsx        # Beat display (140 lines)
│   │                       # - Summary stats
│   │                       # - Edit mode
│   │
│   └── ConfigPanel.tsx     # Configuration (120 lines)
│                           # - YouTube/Pexels toggles
│                           # - API key input
│
├── services/
│   └── api.ts              # API client (100 lines)
│                           # - Type-safe requests
│                           # - Error handling
│
├── types/
│   └── models.ts           # TypeScript interfaces (80 lines)
│                           # - Beat, Config, Asset, etc.
│
└── styles/
    └── index.css           # Tailwind + custom styles (80 lines)
```

## Execution Flow

### Request Lifecycle (Example: Upload)

```
1. User selects file in browser
   └─> ScriptUpload component triggers handleFile()

2. Frontend validates file type
   └─> .md or .txt only

3. Frontend calls uploadScript(file)
   └─> Sends POST /api/upload with multipart form data

4. Browser sends HTTP request
   └─> http://localhost:5000/api/upload

5. Backend Flask receives request
   └─> Routes to /api/upload handler

6. Route handler (upload.py)
   ├─> Validates file
   ├─> Creates session directory
   ├─> Saves file to disk
   ├─> Imports ScriptParser
   └─> Calls parser.parse_file()

7. ScriptParser processes markdown
   ├─> Reads file content
   ├─> Extracts sections (##)
   ├─> Calculates duration
   ├─> Generates keywords
   └─> Returns Beat[] objects

8. Backend converts to JSON
   └─> Returns {sessionId, beats, summary}

9. Frontend receives response
   ├─> Stores sessionId (state)
   ├─> Stores beats (state)
   └─> Navigates to review step

10. User sees parsed beats in BeatList component
```

## State Management Pattern

### Frontend State

Component-level state using React hooks:

```typescript
// In Workflow.tsx
const [currentStep, setCurrentStep] = useState<WorkflowStep>('upload')
const [sessionId, setSessionId] = useState<string | null>(null)
const [beats, setBeats] = useState<Beat[]>([])
const [config, setConfig] = useState<Config>({...})
const [isLoading, setIsLoading] = useState(false)
const [error, setError] = useState<string | null>(null)
const [exportResult, setExportResult] = useState<any>(null)
```

**Note**: For larger apps, consider using Zustand or Context API

### Backend State

File-based session storage:

```python
# In app.py
app.config['SESSION_FOLDER'] = './sessions'

# Session files persist across requests
# Each session gets a unique UUID directory
# state.json stores all workflow state
```

## Error Handling

### Backend Errors

```python
try:
    # Process request
except FileNotFoundError:
    return {'error': 'File not found'}, 404
except ValidationError as e:
    return {'error': f'Validation failed: {str(e)}'}, 400
except Exception as e:
    logger.error(f'Error: {str(e)}', exc_info=True)
    return {'error': 'Internal server error'}, 500
```

### Frontend Errors

```typescript
try {
  const response = await uploadScript(file)
  onUploadSuccess(response)
} catch (err) {
  const message = getErrorMessage(err)
  setError(message)  // Display to user
}
```

## Security Considerations

### File Upload
- ✅ File type validation (.md, .txt only)
- ✅ File size limit (16MB)
- ✅ Filename sanitization
- ✅ Files saved to isolated session directory

### API Access
- ✅ CORS configured (frontend can access backend)
- ✅ Path traversal protection (download endpoint)
- ✅ Session ID validation
- ✅ Input validation on all endpoints

### Data Handling
- ✅ No sensitive data in logs
- ✅ Session cleanup (delete endpoint)
- ✅ File permissions (read-write on session files)

## Performance Considerations

### Frontend
- Vite for fast HMR (hot module reload)
- Lazy component loading (routing)
- Tailwind CSS for optimized styling
- axios for efficient HTTP requests

### Backend
- Flask development server adequate for development
- Use gunicorn for production
- Session data lightweight (JSON)
- No database needed for MVP

## Future Extensibility

### Easy to Add
- [ ] Real-time progress streaming (SSE/WebSocket)
- [ ] Asset preview gallery
- [ ] Project persistence
- [ ] Database backend (PostgreSQL)
- [ ] Authentication/authorization
- [ ] Analytics
- [ ] Batch processing
- [ ] Custom templates

### Architecture Supports
- Multiple concurrent sessions
- Stateless API design
- Modular component structure
- Pluggable services
- Clear separation of concerns

## Deployment Architecture

### Development
```
localhost:5000 (Flask)
    ↑ API calls
localhost:3000 (Vite)
```

### Production
```
nginx (reverse proxy)
├─ /api → Gunicorn (Flask)
└─ / → Nginx static (React dist/)
```

## Monitoring & Debugging

### Backend Debugging
- Flask logs to terminal
- logger.info/error for custom messages
- Enabled in development mode automatically

### Frontend Debugging
- Browser DevTools (F12)
- React DevTools extension
- Network tab for API calls
- Console for error messages

## Summary

The web app is a modular, maintainable system that:
- ✅ Wraps existing CLI functionality
- ✅ Provides intuitive UI
- ✅ Maintains clean architecture
- ✅ Supports easy extensions
- ✅ Includes proper error handling
- ✅ Uses modern tech stack
- ✅ Is production-ready

All code is documented, typed, and follows best practices.
