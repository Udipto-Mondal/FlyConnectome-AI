# Windows PowerShell one-click launcher for FlyConnectome AI
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  FLYCONNECTOME AI — Google Fly Connectome Discovery Engine  " -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if networkx is installed
Write-Host "[1/3] Checking backend Python dependencies..." -ForegroundColor Yellow
python -c "import networkx, fastapi, uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing missing dependencies..." -ForegroundColor Yellow
    pip install -r backend/requirements.txt
}

# Check frontend build
if (-not (Test-Path "frontend/dist/index.html")) {
    Write-Host "[2/3] Building frontend assets..." -ForegroundColor Yellow
    Push-Location frontend
    npm install
    npm run build
    Pop-Location
} else {
    Write-Host "[2/3] Frontend build found in frontend/dist." -ForegroundColor Green
}

Write-Host "[3/3] Launching FlyConnectome AI FastAPI Server on http://localhost:8000 ..." -ForegroundColor Cyan
$env:PYTHONPATH = "$ScriptDir\backend"
python -m uvicorn app.main:app --app-dir "$ScriptDir\backend" --host 0.0.0.0 --port 8000 --reload
