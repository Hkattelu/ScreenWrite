# Running the ScreenWrite Web App

Quick reference for starting the web app for development and testing.

## One-Time Setup

Complete the setup instructions in [SETUP.md](./SETUP.md) first. This only needs to be done once.

## Running (Development)

### Option 1: Using Two Terminals (Recommended)

**Terminal 1 - Backend**:
```bash
cd c:\Users\himan\\code\\ScreenWrite\webapp\backend

# Activate virtual environment
venv\Scripts\activate

# Start Flask server
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

**Terminal 2 - Frontend** (open new terminal while keeping Terminal 1 running):
```bash
cd c:\Users\himan\\code\\ScreenWrite\webapp\frontend

# Start Vite dev server
npm run dev
```

Expected output:
```
  VITE v5.0.0  ready in 500 ms

  âžœ  Local:   http://localhost:3000/
  âžœ  press h to show help
```

### Option 2: Using One Terminal with Background Process

```bash
# Start backend in background
cd c:\Users\himan\\code\\ScreenWrite\webapp\backend
venv\Scripts\activate
python app.py &

# Start frontend in foreground
cd c:\Users\himan\\code\\ScreenWrite\webapp\frontend
npm run dev
```

## Accessing the App

1. **Frontend**: http://localhost:3000
2. **Backend API**: http://localhost:5000/api/health
3. **Backend Swagger** (if added later): http://localhost:5000/api/docs

## Stopping the App

Press `Ctrl+C` in each terminal to stop the servers:
- Backend: `Ctrl+C` in Terminal 1
- Frontend: `Ctrl+C` in Terminal 2

## Testing the App

### 1. Home Page
- Visit http://localhost:3000
- Should see "ScreenWrite" welcome screen
- Click "Get Started" or "Start Building Your Timeline"

### 2. Upload Script
Create `test_script.md`:
```markdown
## Opening
Beautiful sunrise over mountains with
peaceful music and bird sounds setting
the tone for an inspiring video.

## Main Action
Show people working together in an office,
typing, meetings, collaboration and teamwork
between colleagues on different projects.

## Closing
End with sunset over city and team
looking forward to success and growth.
```

- Upload the file
- Should see 3 beats parsed
- Check durations, keywords, and search phrases

### 3. Complete Workflow
- Upload â†’ Review â†’ Configure â†’ Export
- Edit beats if desired
- Configure YouTube/Pexels sources
- Click "Generate Timeline"
- Download FCPXML file

## Verifying Backend Connection

If the frontend can't connect to the backend:

### Check Backend is Running
```bash
# Windows - from any terminal
curl http://localhost:5000/api/health
# or open in browser: http://localhost:5000/api/health
```

Should return:
```json
{"status": "healthy"}
```

### Check Proxy Configuration
- Edit `webapp/frontend/vite.config.ts`
- Verify proxy target is `http://localhost:5000`
- Restart frontend: `npm run dev`

### Check Firewall
- Windows Firewall might block connections
- Allow `python.exe` to access the network

## Monitoring Development

### Backend Logs
- Check Flask terminal for request logs
- Look for `POST /api/upload` and other endpoints
- Errors show in red text

### Frontend Logs
- Check browser console (F12)
- Check Vite terminal for build warnings
- Check Network tab in DevTools for API calls

### File Changes
- Backend: Files auto-reload when saved (Flask debug mode)
- Frontend: Files hot-reload in browser (Vite HMR)

## Common Issues

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Check virtual environment
venv\Scripts\activate
python -m pip show flask  # Should show Flask 3.0.0

# Try reinstalling
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 16+
npm --version   # Should be 8+

# Reinstall
rm -rf node_modules
npm install

# Clear cache
npm cache clean --force
```

### Port conflicts
```bash
# Check what's using the port
netstat -ano | findstr :5000    # Backend port
netstat -ano | findstr :3000    # Frontend port

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### API calls return 404
- Make sure backend Flask server is running
- Check that API endpoint is spelled correctly
- Look in backend logs for the request

### CORS errors in browser console
- Backend is not running on http://localhost:5000
- CORS is not enabled (should be by default in app.py)
- Try hard-refresh (Ctrl+Shift+R) in browser

## Development Tips

### Working on Backend
```bash
# After editing Python files
# Flask auto-reloads if FLASK_ENV=development
# No need to restart manually

# To test API manually:
curl -X POST http://localhost:5000/api/health
```

### Working on Frontend
```bash
# After editing React/TypeScript
# Vite hot-reloads automatically
# Changes appear in browser instantly

# To view compiled output:
# npm run build
# Check dist/ folder
```

### Debugging with Print Statements

**Backend**:
```python
# In app.py or routes
logger.info(f'Debug message: {variable}')
# Shows in Flask terminal
```

**Frontend**:
```typescript
// In components
console.log('Debug:', variable)
// Shows in browser DevTools console (F12)
```

## Building for Production

```bash
# Frontend build
cd webapp/frontend
npm run build
# Creates optimized dist/ folder

# Backend (no build step)
# Just set FLASK_ENV=production and use gunicorn
pip install gunicorn
gunicorn app:app --workers 4
```

## Next Steps

1. âœ… Verify both servers start
2. âœ… Test uploading a script
3. âœ… Test complete workflow
4. âœ… Examine code structure
5. âœ… Start adding features or modifications

## Health Check

Run these to verify everything is working:

```bash
# Test backend
curl http://localhost:5000/api/health
# Expected: {"status": "healthy"}

# Test frontend loads
curl http://localhost:3000
# Expected: HTML page with React app

# Test file upload (requires test_script.md)
curl -F "file=@test_script.md" http://localhost:5000/api/upload
# Expected: JSON with sessionId and beats
```

## Support

- Check [SETUP.md](./SETUP.md) for detailed setup
- Check [README.md](./README.md) for API documentation  
- Check [WEBAPP_SUMMARY.md](../WEBAPP_SUMMARY.md) for architecture
- Check inline code comments

Happy developing!


