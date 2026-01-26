# Web App Architecture

Detailed architecture documentation for the ScreenWrite web app.

## System Overview

The web app is a modern full-stack application that wraps the existing `screenwrite` CLI tool in an intuitive web interface.

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    User's Browser                            â”‚
â”‚                 (http://localhost:3000)                      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                   â”‚ HTTP + JSON
                   â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              Frontend (React + Vite)                         â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚  â”‚ Pages: Home, Workflow                                  â”‚ â”‚
â”‚  â”‚ Components: Upload, BeatList, ConfigPanel             â”‚ â”‚
â”‚  â”‚ Services: API client with axios                        â”‚ â”‚
â”‚  â”‚ Styling: Tailwind CSS                                 â”‚ â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                   â”‚ REST API calls
                   â”‚ /api/upload, /api/session/*, /api/export
                   â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              Backend (Flask + Python)                        â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚  â”‚ Routes:                                                â”‚ â”‚
â”‚  â”‚  - upload.py: Parse scripts into beats               â”‚ â”‚
â”‚  â”‚  - api.py: Session management                         â”‚ â”‚
â”‚  â”‚  - export.py: FCPXML generation                       â”‚ â”‚
â”‚  â”‚                                                        â”‚ â”‚
â”‚  â”‚ Services:                                             â”‚ â”‚
â”‚  â”‚  - Session state (JSON files)                         â”‚ â”‚
â”‚  â”‚  - Configuration management                           â”‚ â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                   â”‚ Python imports
                   â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚         screenwrite (Existing CLI)                      â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚  â”‚ - ScriptParser: markdown â†’ beats                      â”‚ â”‚
â”‚  â”‚ - XMLGenerator: beats â†’ FCPXML                        â”‚ â”‚
â”‚  â”‚ - Beat dataclass: core data structure                 â”‚ â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                   â”‚
                   â–¼
         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
         â”‚  File System    â”‚
         â”‚  sessions/      â”‚
         â”‚  uploads/       â”‚
         â”‚  output/        â”‚
         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## Component Hierarchy

### Frontend Components

```
App.tsx
â”œâ”€â”€ Router (React Router)
â”‚
â”œâ”€â”€ Home page
â”‚   â”œâ”€â”€ Hero section
â”‚   â”œâ”€â”€ Features grid
â”‚   â”œâ”€â”€ Workflow steps
â”‚   â””â”€â”€ Script format guide
â”‚
â””â”€â”€ Workflow page
    â”œâ”€â”€ Step indicator (1. Upload, 2. Review, 3. Configure, 4. Export)
    â”‚
    â”œâ”€â”€ Step 1: Upload
    â”‚   â””â”€â”€ ScriptUpload component
    â”‚       â”œâ”€â”€ Drag-drop zone
    â”‚       â”œâ”€â”€ File input
    â”‚       â””â”€â”€ Error display
    â”‚
    â”œâ”€â”€ Step 2: Review
    â”‚   â””â”€â”€ BeatList component
    â”‚       â”œâ”€â”€ Summary stats
    â”‚       â”œâ”€â”€ Beat display
    â”‚       â””â”€â”€ Edit mode (inline)
    â”‚
    â”œâ”€â”€ Step 3: Configure
    â”‚   â””â”€â”€ ConfigPanel component
    â”‚       â”œâ”€â”€ YouTube toggle
    â”‚       â”œâ”€â”€ Pexels configuration
    â”‚       â””â”€â”€ Output directory
    â”‚
    â””â”€â”€ Step 4: Export
        â”œâ”€â”€ Export confirmation
        â”œâ”€â”€ File download
        â””â”€â”€ Success message
```

## Data Flow

### Upload â†’ Parse Flow

```
User clicks "Choose File"
    â”‚
    â–¼
ScriptUpload component
    â”‚
    â”œâ”€ Validate file type (.md or .txt)
    â”œâ”€ Show loading state
    â”‚
    â–¼
uploadScript() API call
    â”‚
    POST /api/upload
    â”‚
    â–¼
Backend: upload.py
    â”‚
    â”œâ”€ Save file to uploads/ folder
    â”œâ”€ Create session directory
    â”œâ”€ Import ScriptParser
    â”‚
    â–¼
ScriptParser.parse_file()
    â”‚
    â”œâ”€ Read markdown
    â”œâ”€ Extract sections (by ##)
    â”œâ”€ Calculate duration per section
    â”œâ”€ Generate stock keywords
    â”œâ”€ Generate YouTube search phrases
    â”‚
    â–¼
Return Beat[] objects
    â”‚
    â–¼
Backend constructs JSON response
    â”‚
    {
      sessionId: "uuid-here",
      beats: [{id, text, duration, stock_keyword, youtube_phrase}, ...],
      summary: {totalBeats, estimatedDuration, warnings}
    }
    â”‚
    â–¼
Frontend receives response
    â”‚
    â”œâ”€ Extract sessionId (save for later)
    â”œâ”€ Store beats in component state
    â””â”€ Navigate to review step
```

### Session State Management

```
Backend maintains session JSON structure:

sessions/
â”œâ”€â”€ {sessionId}/
â”‚   â”œâ”€â”€ state.json  (Session state file)
â”‚   â”œâ”€â”€ {filename}  (Uploaded script)
â”‚   â”œâ”€â”€ timeline.fcpxml  (Generated output)
â”‚   â””â”€â”€ ...other files

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
    â”‚
    â–¼
Workflow component calls exportFcpxml()
    â”‚
    POST /api/session/{id}/export
    â”‚
    â–¼
Backend: export.py
    â”‚
    â”œâ”€ Load session state
    â”œâ”€ Reconstruct Beat objects from state
    â”œâ”€ Retrieve assets (if available)
    â”‚
    â–¼
XMLGenerator.generate(beats, assets, output_path)
    â”‚
    â”œâ”€ Create FCPXML document structure
    â”œâ”€ Set format (1920x1080, 30fps)
    â”œâ”€ Create media resources
    â”œâ”€ Build timeline spine with gaps
    â”œâ”€ Add B-roll clips to connected lane
    â”‚
    â–¼
Write timeline.fcpxml to disk
    â”‚
    â–¼
Return export info to frontend
    â”‚
    {
      fcpxmlPath: "...",
      downloadUrl: "/api/session/{id}/download/timeline.fcpxml",
      assetCount: 5,
      beatCount: 3,
      estimatedDuration: 42.5
    }
    â”‚
    â–¼
Frontend displays download link
    â”‚
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
â”œâ”€â”€ app.py                  # Main Flask app (70 lines)
â”‚                           # - Flask initialization
â”‚                           # - CORS setup
â”‚                           # - Error handlers
â”‚                           # - Health check endpoint
â”‚
â”œâ”€â”€ routes/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ upload.py           # Upload endpoint (120 lines)
â”‚   â”‚                       # - File validation
â”‚   â”‚                       # - ScriptParser integration
â”‚   â”‚                       # - Session creation
â”‚   â”‚
â”‚   â”œâ”€â”€ api.py              # Session routes (150 lines)
â”‚   â”‚                       # - Get/update session
â”‚   â”‚                       # - Config management
â”‚   â”‚                       # - Status queries
â”‚   â”‚
â”‚   â””â”€â”€ export.py           # Export routes (130 lines)
â”‚                           # - FCPXML generation
â”‚                           # - File download
â”‚
â”œâ”€â”€ requirements.txt        # Python dependencies
â””â”€â”€ .env.example            # Environment template
```

### Frontend (TypeScript/React)

```
webapp/frontend/src/
â”œâ”€â”€ App.tsx                 # Main app component (20 lines)
â”œâ”€â”€ main.tsx                # React DOM render entry
â”‚
â”œâ”€â”€ pages/
â”‚   â”œâ”€â”€ Home.tsx            # Home page (130 lines)
â”‚   â”‚                       # - Welcome screen
â”‚   â”‚                       # - Features overview
â”‚   â”‚                       # - Workflow steps
â”‚   â”‚
â”‚   â””â”€â”€ Workflow.tsx        # Multi-step wizard (200 lines)
â”‚                           # - Step management
â”‚                           # - Upload â†’ Review â†’ Configure â†’ Export
â”‚
â”œâ”€â”€ components/
â”‚   â”œâ”€â”€ ScriptUpload.tsx    # Upload component (100 lines)
â”‚   â”‚                       # - Drag-drop zone
â”‚   â”‚                       # - File validation
â”‚   â”‚
â”‚   â”œâ”€â”€ BeatList.tsx        # Beat display (140 lines)
â”‚   â”‚                       # - Summary stats
â”‚   â”‚                       # - Edit mode
â”‚   â”‚
â”‚   â””â”€â”€ ConfigPanel.tsx     # Configuration (120 lines)
â”‚                           # - YouTube/Pexels toggles
â”‚                           # - API key input
â”‚
â”œâ”€â”€ services/
â”‚   â””â”€â”€ api.ts              # API client (100 lines)
â”‚                           # - Type-safe requests
â”‚                           # - Error handling
â”‚
â”œâ”€â”€ types/
â”‚   â””â”€â”€ models.ts           # TypeScript interfaces (80 lines)
â”‚                           # - Beat, Config, Asset, etc.
â”‚
â””â”€â”€ styles/
    â””â”€â”€ index.css           # Tailwind + custom styles (80 lines)
```

## Execution Flow

### Request Lifecycle (Example: Upload)

```
1. User selects file in browser
   â””â”€> ScriptUpload component triggers handleFile()

2. Frontend validates file type
   â””â”€> .md or .txt only

3. Frontend calls uploadScript(file)
   â””â”€> Sends POST /api/upload with multipart form data

4. Browser sends HTTP request
   â””â”€> http://localhost:5000/api/upload

5. Backend Flask receives request
   â””â”€> Routes to /api/upload handler

6. Route handler (upload.py)
   â”œâ”€> Validates file
   â”œâ”€> Creates session directory
   â”œâ”€> Saves file to disk
   â”œâ”€> Imports ScriptParser
   â””â”€> Calls parser.parse_file()

7. ScriptParser processes markdown
   â”œâ”€> Reads file content
   â”œâ”€> Extracts sections (##)
   â”œâ”€> Calculates duration
   â”œâ”€> Generates keywords
   â””â”€> Returns Beat[] objects

8. Backend converts to JSON
   â””â”€> Returns {sessionId, beats, summary}

9. Frontend receives response
   â”œâ”€> Stores sessionId (state)
   â”œâ”€> Stores beats (state)
   â””â”€> Navigates to review step

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
- âœ… File type validation (.md, .txt only)
- âœ… File size limit (16MB)
- âœ… Filename sanitization
- âœ… Files saved to isolated session directory

### API Access
- âœ… CORS configured (frontend can access backend)
- âœ… Path traversal protection (download endpoint)
- âœ… Session ID validation
- âœ… Input validation on all endpoints

### Data Handling
- âœ… No sensitive data in logs
- âœ… Session cleanup (delete endpoint)
- âœ… File permissions (read-write on session files)

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
    â†‘ API calls
localhost:3000 (Vite)
```

### Production
```
nginx (reverse proxy)
â”œâ”€ /api â†’ Gunicorn (Flask)
â””â”€ / â†’ Nginx static (React dist/)
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
- âœ… Wraps existing CLI functionality
- âœ… Provides intuitive UI
- âœ… Maintains clean architecture
- âœ… Supports easy extensions
- âœ… Includes proper error handling
- âœ… Uses modern tech stack
- âœ… Is production-ready

All code is documented, typed, and follows best practices.


