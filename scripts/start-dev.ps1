# =============================================================================
# Development Startup Script - Propositional Logic Trainer
# =============================================================================
# Startet Frontend (React) und Backend (Django) parallel
#
# Verwendung: .\scripts\start-dev.ps1
# =============================================================================

Write-Host "Starting Propositional Logic Trainer..." -ForegroundColor Cyan
Write-Host ""

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRootPath = $RepoRoot.Path

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js ist nicht installiert!" -ForegroundColor Red
    Write-Host "   Bitte installiere Node.js von https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if npm is installed
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "npm ist nicht installiert oder nicht im PATH!" -ForegroundColor Red
    Write-Host "   Bitte installiere Node.js von https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if Python virtual environment exists
if (-not (Test-Path (Join-Path $RepoRootPath ".venv"))) {
    Write-Host "Virtual Environment nicht gefunden!" -ForegroundColor Red
    Write-Host "   Bitte führe zuerst setup.sh aus" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if node_modules exists, if not run npm install
if (-not (Test-Path (Join-Path $RepoRootPath "frontend\node_modules"))) {
    Write-Host "Installiere Frontend Dependencies..." -ForegroundColor Yellow
    Set-Location (Join-Path $RepoRootPath "frontend")
    npm install
    Set-Location $RepoRootPath
    Write-Host "Frontend Dependencies installiert" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Starte beide Services:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "   API:      http://localhost:8000/api/" -ForegroundColor Green
Write-Host "   Admin:    http://localhost:8000/admin/" -ForegroundColor Green
Write-Host ""
Write-Host "Beide Terminal-Fenster offen lassen!" -ForegroundColor Yellow
Write-Host "   Drücke Strg+C in jedem Fenster zum Stoppen" -ForegroundColor Yellow
Write-Host ""

# Start Backend in new window
Write-Host "Starte Backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    Write-Host '=== Django Backend ===' -ForegroundColor Cyan;
    Set-Location '$RepoRootPath';
    .\.venv\Scripts\Activate.ps1;
    Write-Host 'Virtual Environment aktiviert' -ForegroundColor Green;
    python manage.py runserver;
"

# Wait a bit for backend to start
Start-Sleep -Seconds 2

# Start Frontend in new window
Write-Host "Starte Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    Write-Host '=== React Frontend ===' -ForegroundColor Cyan;
    Set-Location '$RepoRootPath\frontend';
    Write-Host 'Starte Vite Dev Server' -ForegroundColor Green;
    npm run dev;
"

Write-Host ""
Write-Host "Services gestartet!" -ForegroundColor Green
Write-Host "   Zwei neue Terminal-Fenster sollten geöffnet sein" -ForegroundColor Green
Write-Host "   Öffne http://localhost:5173 im Browser" -ForegroundColor Cyan
Write-Host ""
