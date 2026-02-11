# screenwrite Development Runner (Windows)

Write-Host "Starting ScreenWrite in development mode..." -ForegroundColor Cyan

# Check if venv exists
if (!(Test-Path "venv")) {
    Write-Host "Error: Virtual environment not found. Please run ./setup.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "1. Starting Backend (Flask) on http://localhost:5000" -ForegroundColor Green
# Start backend in a separate terminal window so logs are visible
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '--- SCREENWRITE BACKEND ---' -ForegroundColor Cyan; cd webapp/backend; & ..\..\venv\Scripts\python app.py"

Write-Host "2. Starting Frontend (Vite) on http://localhost:3000" -ForegroundColor Green
# Start frontend in the current process
Push-Location webapp\frontend
npm run dev
Pop-Location
