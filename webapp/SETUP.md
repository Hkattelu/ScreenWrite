# Footage Web App Setup Guide

Complete step-by-step instructions for setting up the web app locally for development.

## Prerequisites

Before starting, ensure you have:

1. **Python 3.8+** installed
   ```bash
   python --version
   ```

2. **Node.js 16+ and npm** installed
   ```bash
   node --version
   npm --version
   ```

3. **Git** (for cloning if needed)

## Step 1: Backend Setup

### 1.1 Navigate to backend directory
```bash
cd webapp/backend
```

### 1.2 Create Python virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Upgrade pip
```bash
pip install --upgrade pip
```

### 1.4 Install Python dependencies
```bash
pip install -r requirements.txt
```

### 1.5 Create .env file (optional, but recommended)
```bash
# Copy example
cp .env.example .env

# Edit if needed (usually defaults are fine)
# FLASK_ENV=development
# FLASK_PORT=5000
```

### 1.6 Test backend startup
```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

Press `Ctrl+C` to stop. Keep this terminal open for the next step.

## Step 2: Frontend Setup

### 2.1 Open a new terminal and navigate to frontend directory
```bash
cd webapp/frontend
```

### 2.2 Install Node.js dependencies
```bash
npm install
```

This creates a `node_modules/` directory and installs all packages listed in `package.json`.

### 2.3 Start development server
```bash
npm run dev
```

You should see:
```
  VITE v5.0.0  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  press h to show help
```

## Step 3: Verify Everything Works

1. **Open browser**: Visit http://localhost:3000
2. **See the home page**: You should see the Footage welcome screen
3. **Click "Get Started"**: Navigate to the workflow page
4. **Test upload**: Try uploading a sample markdown file

### Sample test script
Create `test_script.md`:
```markdown
## Introduction
This is an opening scene showing a beautiful sunrise
over mountains with birds flying. Very peaceful and
inspiring to set the tone for the video.

## Main Content
Show people working together in a modern office
environment. Quick cuts of typing, meetings, and
collaboration between team members.

## Conclusion
End with an inspiring shot of the team looking
out over the city at sunset with hope for the future.
```

Upload this file and verify:
- ✅ File uploads successfully
- ✅ Beats are parsed (should have 3 beats)
- ✅ Durations are calculated
- ✅ Can click through to Review and Configure steps

## Troubleshooting

### Backend issues

**Port 5000 already in use**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>
```

**ModuleNotFoundError: No module named 'flask'**
- Ensure virtual environment is activated: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
- Reinstall dependencies: `pip install -r requirements.txt`

**CORS errors**
- Backend is not running on http://localhost:5000
- Check that Flask server is started and showing "Running on http://127.0.0.1:5000"

### Frontend issues

**Module not found errors**
```bash
npm install
```

**Port 3000 already in use**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :3000
kill -9 <PID>
```

**Vite is slow**
- This is normal on first run
- Subsequent builds will be faster due to caching

## Development Workflow

### Terminal Setup
Keep two terminals open:

**Terminal 1: Backend**
```bash
cd webapp/backend
source venv/bin/activate    # activate virtual env
python app.py
```

**Terminal 2: Frontend**
```bash
cd webapp/frontend
npm run dev
```

### Making Changes

**Backend**:
- Edit files in `webapp/backend/`
- Flask auto-reloads on file changes (if FLASK_ENV=development)
- Test with Postman or curl

**Frontend**:
- Edit files in `webapp/frontend/src/`
- Vite hot-reloads automatically in the browser
- See changes instantly

### Adding Dependencies

**Backend**:
```bash
cd webapp/backend
source venv/bin/activate
pip install package_name
pip freeze > requirements.txt  # Update requirements
```

**Frontend**:
```bash
cd webapp/frontend
npm install package-name
# package.json is updated automatically
```

## Next Steps

1. **Explore the codebase**:
   - Backend routes in `webapp/backend/routes/`
   - Frontend components in `webapp/frontend/src/components/`
   - API client in `webapp/frontend/src/services/api.ts`

2. **Read the architecture**:
   - See `webapp/README.md` for architecture overview
   - Review API endpoint specs

3. **Build features**:
   - Add real-time progress tracking (SSE)
   - Implement asset preview gallery
   - Add project persistence

4. **Test thoroughly**:
   - Test with various markdown scripts
   - Test error scenarios (bad files, network errors)
   - Test with actual DaVinci Resolve import

## Useful Commands

### Backend
```bash
# Run server
python app.py

# Run with debugging
python app.py --debug

# Check syntax
python -m py_compile routes/upload.py
```

### Frontend
```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npm run type-check

# Lint code
npm run lint
```

## Production Deployment

See [README.md](./README.md#deployment) for production deployment instructions.

## Getting Help

1. Check terminal error messages - they're usually very descriptive
2. Ensure both backend and frontend servers are running
3. Open browser DevTools (F12) to check for frontend errors
4. Check Flask logs for backend errors
5. Review the main [README.md](./README.md) for FAQs

## Common Development Tasks

### Debugging Backend
```python
# Add print statements or use Python debugger
import pdb; pdb.set_trace()

# Or use Flask debugger (already enabled in development mode)
```

### Debugging Frontend
- Use browser DevTools (F12)
- React Developer Tools extension for Chrome/Firefox
- Check Network tab for API calls

### Testing API manually
```bash
# Using curl
curl -X POST http://localhost:5000/api/health

# Or use Postman (UI tool for API testing)
# Download from postman.com
```

## Success!

You should now have:
- ✅ Backend running on http://localhost:5000
- ✅ Frontend running on http://localhost:3000
- ✅ Hot-reloading for both backend and frontend
- ✅ Ready to develop new features

Happy coding!
