$ErrorActionPreference = "Stop"

# 1. Activate Virtual Environment
Write-Host "Activating 'auto_mail' virtual environment..." -ForegroundColor Cyan
& ".\auto_mail\Scripts\Activate.ps1"

# 2. Validation
if (!(Test-Path "token.json") -and !(Test-Path "token_debug.json")) {
    Write-Host "WARNING: No token.json found. You may need to run authentication first." -ForegroundColor Yellow
    Write-Host "Try running: python src/debug_auth.py --run" -ForegroundColor Yellow
    exit
}

# 3. Run the Agent as a Module
# This fixes the 'ModuleNotFoundError: No module named src' error
Write-Host "Starting Agent (src.main)..." -ForegroundColor Green
python -m src.main
