#!/bin/bash
# =============================================================================
# Setup-Skript - Propositional Logic Trainer (Bash)
# =============================================================================
# Erstellt virtuelle Umgebung und installiert alle Dependencies
#
# Verwendung: ./scripts/setup.sh
# =============================================================================

# Farben fuer Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # Keine Farbe

echo -e "${CYAN}Setup - Propositional Logic Trainer${NC}"
echo ""

# Wechsle ins Repository-Root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# Mache alle Shell-Skripte ausfuehrbar (fuer zukuenftige Aufrufe)
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true

# ---------------------------------------------------------
# Pruefe ob uv installiert ist
# ---------------------------------------------------------
if ! command -v uv &> /dev/null; then
    echo -e "${RED}uv ist nicht installiert!${NC}"
    echo -e "${YELLOW}   Installiere uv: https://docs.astral.sh/uv/getting-started/installation/${NC}"
    echo -e "${YELLOW}   curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi

# ---------------------------------------------------------
# Lade Python-Version aus .python-version
# ---------------------------------------------------------
if [ ! -f ".python-version" ]; then
    echo -e "${RED}.python-version Datei nicht gefunden!${NC}"
    echo -e "${YELLOW}   Bitte lege eine Datei '.python-version' im Projektverzeichnis an.${NC}"
    exit 1
fi

# Lese Version und entferne Whitespace/Newlines
PYTHON_VERSION=$(cat .python-version | tr -d '[:space:]')

echo -e "${CYAN}>>> Verwende Python-Version $PYTHON_VERSION${NC}"

# ---------------------------------------------------------
# Installiere Python-Version via uv
# ---------------------------------------------------------
echo -e "${CYAN}>>> Installiere Python-Version $PYTHON_VERSION${NC}"
uv python install "$PYTHON_VERSION"

# ---------------------------------------------------------
# Loesche existierende virtuelle Umgebung
# ---------------------------------------------------------
if [ -d ".venv" ]; then
    echo -e "${CYAN}>>> Loesche existierende virtuelle Umgebung...${NC}"
    if ! rm -rf .venv 2>/dev/null; then
        echo ""
        echo -e "${RED}FEHLER: .venv Verzeichnis konnte nicht geloescht werden!${NC}"
        echo -e "${YELLOW}Wahrscheinlich wird python von einem anderen Prozess verwendet.${NC}"
        echo ""
        echo -e "${CYAN}Loesung:${NC}"
        echo "   1. Schliesse alle Terminals (auch in VS Code)"
        echo "   2. Oder starte VS Code neu und fuehre das Script erneut aus"
        echo ""
        exit 1
    fi
fi

# ---------------------------------------------------------
# Fixiere Python-Version und erstelle venv
# ---------------------------------------------------------
echo -e "${CYAN}>>> Fixiere Python-Version${NC}"
uv python pin "$PYTHON_VERSION"

echo -e "${CYAN}>>> Erstelle neue virtuelle Umgebung${NC}"
uv venv --python "$PYTHON_VERSION"

# ---------------------------------------------------------
# Aktiviere virtuelle Umgebung
# ---------------------------------------------------------
echo -e "${CYAN}>>> Aktiviere virtuelle Umgebung...${NC}"

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash)
    source .venv/Scripts/activate
else
    # macOS oder Linux
    source .venv/bin/activate
fi

# ---------------------------------------------------------
# Installiere Dependencies aus requirements.txt
# ---------------------------------------------------------
echo -e "${CYAN}>>> Installiere Projekt-Dependencies${NC}"
uv pip install --override requirements.txt -r requirements.txt

# ---------------------------------------------------------
# Loesche uv Lock-Datei (Projekt verwendet requirements.txt)
# ---------------------------------------------------------
echo -e "${CYAN}>>> Loesche uv Lock-Dateien (falls vorhanden)${NC}"
rm -f uv.lock

# ---------------------------------------------------------
# Fuehre Django-Migrationen aus
# ---------------------------------------------------------
echo -e "${CYAN}>>> Fuehre Django-Migrationen aus...${NC}"
python manage.py makemigrations --noinput
python manage.py migrate

echo ""
echo -e "${GREEN}Setup erfolgreich abgeschlossen!${NC}"
echo ""

