# =============================================================================
# Entwicklungs-Startskript - Propositional Logic Trainer
# =============================================================================
# Startet Frontend (React) und Backend (Django) parallel
#
# Verwendung: .\scripts\start-dev.ps1
# =============================================================================

Write-Host "Starte Propositional Logic Trainer..." -ForegroundColor Cyan
Write-Host ""

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRootPath = $RepoRoot.Path

# Pruefe ob Node.js installiert ist
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js ist nicht installiert!" -ForegroundColor Red
    Write-Host "   Bitte installiere Node.js von https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Pruefe ob npm installiert ist
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "npm ist nicht installiert oder nicht im PATH!" -ForegroundColor Red
    Write-Host "   Bitte installiere Node.js von https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Pruefe ob virtuelle Python-Umgebung existiert
if (-not (Test-Path (Join-Path $RepoRootPath ".venv"))) {
    Write-Host "Virtuelle Umgebung nicht gefunden!" -ForegroundColor Red
    Write-Host "   Bitte fuehre zuerst setup.ps1 aus" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Pruefe ob node_modules existiert, falls nicht npm install ausfuehren
if (-not (Test-Path (Join-Path $RepoRootPath "frontend\node_modules"))) {
    Write-Host "Installiere Frontend-Dependencies..." -ForegroundColor Yellow
    Set-Location (Join-Path $RepoRootPath "frontend")
    npm install
    Set-Location $RepoRootPath
    Write-Host "Frontend-Dependencies installiert" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Starte beide Services:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "   API:      http://localhost:8000/api/" -ForegroundColor Green
Write-Host "   Admin:    http://localhost:8000/admin/" -ForegroundColor Green
Write-Host ""
Write-Host "Beide Terminal-Fenster offen lassen!" -ForegroundColor Yellow
Write-Host "   Druecke Strg+C in jedem Fenster zum Stoppen" -ForegroundColor Yellow
Write-Host ""

# Starte Backend in neuem Fenster
Write-Host "Starte Backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    Write-Host '=== Django Backend ===' -ForegroundColor Cyan;
    Set-Location '$RepoRootPath';
    .\.venv\Scripts\Activate.ps1;
    Write-Host 'Virtuelle Umgebung aktiviert' -ForegroundColor Green;
    python manage.py runserver;
"

# Warte kurz bis Backend gestartet ist
Start-Sleep -Seconds 2

# Starte Frontend in neuem Fenster
Write-Host "Starte Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    Write-Host '=== React Frontend ===' -ForegroundColor Cyan;
    Set-Location '$RepoRootPath\frontend';
    Write-Host 'Starte Vite Dev Server' -ForegroundColor Green;
    npm run dev;
"

Write-Host ""
Write-Host "Services gestartet!" -ForegroundColor Green
Write-Host "   Zwei neue Terminal-Fenster sollten geoeffnet sein" -ForegroundColor Green
Write-Host "   Oeffne http://localhost:5173 im Browser" -ForegroundColor Cyan
Write-Host ""
