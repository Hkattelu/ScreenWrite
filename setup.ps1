# screenwrite Unified Setup Script (Windows)

Write-Host "Starting screenwrite setup..." -ForegroundColor Cyan

# 1. Check for Python and Node.js
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    exit 1
}
if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Node.js/npm is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# 2. Create Virtual Environment
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# 3. Activate venv and install dependencies
Write-Host "Installing Python dependencies (Core + Backend)..."
& .\venv\Scripts\pip install -e .
& .\venv\Scripts\pip install -r webapp\backend\requirements.txt

# 4. Frontend dependencies
if (Test-Path "webapp\frontend") {
    Write-Host "Installing frontend dependencies..."
    Push-Location webapp\frontend
    npm install
    Pop-Location
}

# 5. Run onboarding wizard
Write-Host "Running onboarding wizard..."
& .\venv\Scripts\python onboarding.py

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "To run the application in development mode, use:" -ForegroundColor Cyan
Write-Host "  ./run_dev.ps1" -ForegroundColor Yellow