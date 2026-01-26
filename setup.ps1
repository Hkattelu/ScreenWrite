# ScreenWrite One-Command Setup & Launch (Windows)
# This script installs dependencies and starts both Backend and Frontend.

Write-Host "🎬 Initializing ScreenWrite..." -ForegroundColor Cyan

# 1. Check for Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Please install Python 3.10+ from python.org" -ForegroundColor Red
    exit
}

# 2. Check for Node.js
if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js/npm not found. Please install Node.js from nodejs.org" -ForegroundColor Red
    exit
}

# 3. Setup Backend
Write-Host "📦 Setting up Backend..." -ForegroundColor Yellow
cd webapp/backend
if (!(Test-Path venv)) {
    python -m venv venv
}
.\venv\Scripts\pip install -r requirements.txt
if (!(Test-Path .env)) {
    Copy-Item .env.example .env
}
cd ../..

# 4. Setup Frontend
Write-Host "📦 Setting up Frontend..." -ForegroundColor Yellow
cd webapp/frontend
npm install
cd ../..

# 5. Launch both
Write-Host "🚀 Launching ScreenWrite Engines..." -ForegroundColor Green
Write-Host "💡 Backend will run on http://localhost:5000" -ForegroundColor Gray
Write-Host "💡 Frontend will run on http://localhost:3000" -ForegroundColor Gray

# Start Backend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd webapp/backend; .\venv\Scripts\python app.py"

# Start Frontend in current window (will block)
cd webapp/frontend
npm run dev
