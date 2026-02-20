# =============================================================================
# Production Build & Serve Script - Propositional Logic Trainer
# =============================================================================
# Baut das Frontend und serviert es zusammen mit dem Backend über Django
#
# Verwendung: .\scripts\start-production.ps1
# =============================================================================

Write-Host "Production Build - Propositional Logic Trainer" -ForegroundColor Cyan
Write-Host ""

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRootPath = $RepoRoot.Path

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js ist nicht installiert!" -ForegroundColor Red
    Write-Host "   Bitte installiere Node.js von https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check if npm is installed
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "npm ist nicht installiert oder nicht im PATH!" -ForegroundColor Red
    Write-Host "   Bitte installiere Node.js von https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path (Join-Path $RepoRootPath ".venv"))) {
    Write-Host "Virtual Environment nicht gefunden!" -ForegroundColor Red
    Write-Host "   Bitte führe zuerst setup.sh aus" -ForegroundColor Yellow
    exit 1
}

# Build Frontend
Write-Host "Baue Frontend..." -ForegroundColor Yellow
Set-Location (Join-Path $RepoRootPath "frontend")

if (-not (Test-Path "node_modules")) {
    Write-Host "   Installiere Dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "   Starte Build-Prozess..." -ForegroundColor Yellow
npm run build

if (-not (Test-Path "dist")) {
    Write-Host "❌ Build fehlgeschlagen!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..
Write-Host "Frontend gebaut: frontend/dist/" -ForegroundColor Green
Write-Host ""

# Copy built files to Django static directory
Write-Host "Kopiere statische Dateien..." -ForegroundColor Yellow
if (-not (Test-Path (Join-Path $RepoRootPath "staticfiles\frontend"))) {
    New-Item -ItemType Directory -Path (Join-Path $RepoRootPath "staticfiles\frontend") -Force | Out-Null
}
Copy-Item -Path (Join-Path $RepoRootPath "frontend\dist\*") -Destination (Join-Path $RepoRootPath "staticfiles\frontend\") -Recurse -Force
Write-Host "Dateien kopiert nach staticfiles/frontend/" -ForegroundColor Green
Write-Host ""

# Collect Django static files
Write-Host "Django collectstatic..." -ForegroundColor Yellow
Set-Location $RepoRootPath
.\.venv\Scripts\Activate.ps1
python manage.py collectstatic --noinput
Write-Host "Statische Dateien gesammelt" -ForegroundColor Green
Write-Host ""

# Start Django server
Write-Host "Starte Django Server..." -ForegroundColor Cyan
Write-Host "   Server laeuft auf: http://localhost:8000" -ForegroundColor Green
Write-Host "   API:               http://localhost:8000/api/" -ForegroundColor Green
Write-Host "   Admin:             http://localhost:8000/admin/" -ForegroundColor Green
Write-Host ""
Write-Host "Druecke Strg+C zum Stoppen" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver
