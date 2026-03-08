# =============================================================================
# Setup-Skript - Propositional Logic Trainer (Windows PowerShell)
# =============================================================================
# Erstellt virtuelle Umgebung und installiert alle Dependencies
#
# Verwendung: .\scripts\setup.ps1
# =============================================================================

Write-Host "Setup - Propositional Logic Trainer" -ForegroundColor Cyan
Write-Host ""

# Wechsle ins Repository-Root
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

# ---------------------------------------------------------
# Pruefe ob uv installiert ist
# ---------------------------------------------------------
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv ist nicht installiert!" -ForegroundColor Red
    Write-Host "   Installiere uv: https://docs.astral.sh/uv/getting-started/installation/" -ForegroundColor Yellow
    Write-Host "   Windows: powershell -ExecutionPolicy ByPass -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor Yellow
    exit 1
}

# ---------------------------------------------------------
# Lade Python-Version aus .python-version
# ---------------------------------------------------------
if (-not (Test-Path ".python-version")) {
    Write-Host ".python-version Datei nicht gefunden!" -ForegroundColor Red
    Write-Host "   Bitte lege eine Datei '.python-version' im Projektverzeichnis an." -ForegroundColor Yellow
    exit 1
}

$PYTHON_VERSION = (Get-Content ".python-version").Trim()
Write-Host ">>> Verwende Python-Version $PYTHON_VERSION" -ForegroundColor Cyan

# ---------------------------------------------------------
# Installiere Python-Version via uv
# ---------------------------------------------------------
Write-Host ">>> Installiere Python-Version $PYTHON_VERSION" -ForegroundColor Cyan
uv python install $PYTHON_VERSION

# ---------------------------------------------------------
# Loesche existierende virtuelle Umgebung
# ---------------------------------------------------------
if (Test-Path ".venv") {
    Write-Host ">>> Loesche existierende virtuelle Umgebung..." -ForegroundColor Cyan
    try {
        Remove-Item -Recurse -Force ".venv" -ErrorAction Stop
    }
    catch {
        Write-Host ""
        Write-Host "FEHLER: .venv Verzeichnis konnte nicht geloescht werden!" -ForegroundColor Red
        Write-Host "Wahrscheinlich wird python.exe von einem anderen Prozess verwendet." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Loesung:" -ForegroundColor Cyan
        Write-Host "   1. Schliesse alle Terminals (auch in VS Code)" -ForegroundColor White
        Write-Host "   2. In VS Code: Ctrl+Shift+P -> 'Python: Clear Cache and Reload Window'" -ForegroundColor White
        Write-Host "   3. Oder schliesse VS Code komplett und fuehre das Script erneut aus" -ForegroundColor White
        Write-Host ""
        exit 1
    }
}

# ---------------------------------------------------------
# Fixiere Python-Version und erstelle venv
# ---------------------------------------------------------
Write-Host ">>> Fixiere Python-Version" -ForegroundColor Cyan
uv python pin $PYTHON_VERSION

Write-Host ">>> Erstelle neue virtuelle Umgebung" -ForegroundColor Cyan
uv venv --python $PYTHON_VERSION

# ---------------------------------------------------------
# Aktiviere virtuelle Umgebung
# ---------------------------------------------------------
Write-Host ">>> Aktiviere virtuelle Umgebung..." -ForegroundColor Cyan
& ".\.venv\Scripts\Activate.ps1"

# ---------------------------------------------------------
# Installiere Dependencies aus requirements.txt
# ---------------------------------------------------------
Write-Host ">>> Installiere Projekt-Dependencies" -ForegroundColor Cyan
uv pip install --override requirements.txt -r requirements.txt

# ---------------------------------------------------------
# Loesche uv Lock-Datei (Projekt verwendet requirements.txt)
# ---------------------------------------------------------
Write-Host ">>> Loesche uv Lock-Dateien (falls vorhanden)" -ForegroundColor Cyan
Remove-Item -Force "uv.lock" -ErrorAction SilentlyContinue

# ---------------------------------------------------------
# Fuehre Django-Migrationen aus
# ---------------------------------------------------------
Write-Host ">>> Fuehre Django-Migrationen aus..." -ForegroundColor Cyan
python manage.py makemigrations --noinput
python manage.py migrate

Write-Host ""
Write-Host "Setup erfolgreich abgeschlossen!" -ForegroundColor Green
Write-Host ""

