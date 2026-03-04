# =============================================================================
# Produktions-Startskript - Propositional Logic Trainer
# =============================================================================
# Baut das Frontend und serviert es zusammen mit dem Backend ueber Django
#
# Verwendung: .\scripts\start-production.ps1
# =============================================================================

Write-Host "Produktions-Build - Propositional Logic Trainer" -ForegroundColor Cyan
Write-Host ""

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRootPath = $RepoRoot.Path

# Pruefe ob Node.js installiert ist
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js ist nicht installiert!" -ForegroundColor Red
    Write-Host "   Bitte installiere Node.js von https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Pruefe ob npm installiert ist
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "npm ist nicht installiert oder nicht im PATH!" -ForegroundColor Red
    Write-Host "   Bitte installiere Node.js von https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Pruefe ob virtuelle Umgebung existiert
if (-not (Test-Path (Join-Path $RepoRootPath ".venv"))) {
    Write-Host "Virtuelle Umgebung nicht gefunden!" -ForegroundColor Red
    Write-Host "   Bitte fuehre zuerst setup.ps1 aus" -ForegroundColor Yellow
    exit 1
}

# Baue Frontend
Write-Host "Baue Frontend..." -ForegroundColor Yellow
Set-Location (Join-Path $RepoRootPath "frontend")

if (-not (Test-Path "node_modules")) {
    Write-Host "   Installiere Dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "   Starte Build-Prozess..." -ForegroundColor Yellow
npm run build

if (-not (Test-Path "dist")) {
    Write-Host "Build fehlgeschlagen!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..
Write-Host "Frontend gebaut: frontend/dist/" -ForegroundColor Green
Write-Host ""

# Kopiere gebaute Dateien ins Django Static-Verzeichnis
Write-Host "Kopiere statische Dateien..." -ForegroundColor Yellow
if (-not (Test-Path (Join-Path $RepoRootPath "staticfiles\frontend"))) {
    New-Item -ItemType Directory -Path (Join-Path $RepoRootPath "staticfiles\frontend") -Force | Out-Null
}
Copy-Item -Path (Join-Path $RepoRootPath "frontend\dist\*") -Destination (Join-Path $RepoRootPath "staticfiles\frontend\") -Recurse -Force
Write-Host "Dateien kopiert nach staticfiles/frontend/" -ForegroundColor Green
Write-Host ""

# Sammle Django Static-Dateien
Write-Host "Django collectstatic..." -ForegroundColor Yellow
Set-Location $RepoRootPath
.\.venv\Scripts\Activate.ps1
python manage.py collectstatic --noinput
Write-Host "Statische Dateien gesammelt" -ForegroundColor Green
Write-Host ""

# Starte Django-Server
Write-Host "Starte Produktions-Server (Waitress)..." -ForegroundColor Cyan
Write-Host "   Server laeuft auf: http://localhost:8000" -ForegroundColor Green
Write-Host ""
Write-Host "Druecke Strg+C zum Stoppen" -ForegroundColor Yellow
Write-Host ""

# Waitress als Produktions-WSGI-Server (Windows-kompatibel)
python -m waitress --host=127.0.0.1 --port=8000 logic_trainer.wsgi:application
