# --- Configuration ---
$PromptFile = "ralph-prompt.md"
$StatusFile = "ralph-status.txt"

Write-Host "--- Starting Ralph Pattern Loop ---" -ForegroundColor Cyan
Write-Host "Reading from: $PromptFile"
Write-Host "Updating status in: $StatusFile"
Write-Host "Press Ctrl+C to stop the loop." -ForegroundColor Yellow
Write-Host "----------------------------------"

# Ensure the status file exists
if (!(Test-Path $StatusFile)) { New-Item $StatusFile -ItemType File }

while ($true) {
    Write-Host "Sending prompt to Gemini..." -NoNewline
    
    # 1. Read the prompt content
    $CurrentPrompt = Get-Content -Path $PromptFile -Raw

    # 2. Execute Gemini CLI
    # This assumes 'gemini' is in your PATH. 
    # We pipe the prompt and capture the output.
    $Response = $CurrentPrompt | gemini prompt

    # 3. Timestamp the entry and append to status file
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $Entry = "`n`n--- Update: $Timestamp ---`n$Response"
    
    Add-Content -Path $StatusFile -Value $Entry

    Write-Host " Done." -ForegroundColor Green
    Write-Host "Response appended to $StatusFile"

    # 4. Wait for a moment before checking for changes or re-running
    # Adjust the sleep time (in seconds) as needed for your workflow
    Start-Sleep -Seconds 10
}