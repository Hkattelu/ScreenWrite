# Creates the "ScreenWrite" Desktop shortcut (and prepares everything it needs).
# Run once from anywhere:  powershell -ExecutionPolicy Bypass -File create_shortcut.ps1

$ErrorActionPreference = "Stop"

$desktopDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$repoRoot   = Split-Path -Parent $desktopDir
$mainCheckout = "C:\Users\himan\code\footage"
$venvPythonw = Join-Path $mainCheckout "venv\Scripts\pythonw.exe"
$venvPython  = Join-Path $mainCheckout "venv\Scripts\python.exe"

if (-not (Test-Path $venvPythonw)) {
    Write-Error "venv not found at $venvPythonw - run setup.ps1 first."
}

# 1. Build the UI if it hasn't been built yet.
$distIndex = Join-Path $desktopDir "frontend\dist\index.html"
if (-not (Test-Path $distIndex)) {
    Write-Host "Building the UI (one-time)..."
    Push-Location (Join-Path $desktopDir "frontend")
    npm install --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { Pop-Location; Write-Error "npm install failed" }
    npm run build
    if ($LASTEXITCODE -ne 0) { Pop-Location; Write-Error "npm run build failed" }
    Pop-Location
}

# 2. Make sure pywebview is installed in the venv.
& $venvPython -c "import webview" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing pywebview into the venv..."
    & $venvPython -m pip install "pywebview>=5.0" --quiet
}

# 3. Create the Desktop shortcut.
$shortcutPath = Join-Path ([Environment]::GetFolderPath("Desktop")) "ScreenWrite.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $venvPythonw
$shortcut.Arguments = "`"$(Join-Path $desktopDir 'ScreenWrite.pyw')`""
$shortcut.WorkingDirectory = $repoRoot
$shortcut.Description = "ScreenWrite - script to Resolve timeline"
$shortcut.Save()

Write-Host ""
Write-Host "Done. Double-click 'ScreenWrite' on your Desktop to launch." -ForegroundColor Green
