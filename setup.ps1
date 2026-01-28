# screenwrite Unified Setup Script (Windows)

Write-Host "Starting screenwrite setup..." -ForegroundColor Cyan

# 1. Create Virtual Environment
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# 2. Activate venv and install dependencies
Write-Host "Installing Python dependencies..."
& .\venv\Scripts\pip install -r requirements.txt

# 3. Frontend dependencies
if (Test-Path "webapp\frontend") {
    Write-Host "Installing frontend dependencies..."
    Push-Location webapp\frontend
    npm install
    Pop-Location
}

# 4. Run onboarding wizard
& .\venv\Scripts\python onboarding.py