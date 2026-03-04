#!/bin/bash
# =============================================================================
# Produktions-Startskript - Propositional Logic Trainer
# =============================================================================
# Baut das Frontend und serviert es zusammen mit dem Backend ueber Django
#
# Verwendung: ./scripts/start-production.sh
# =============================================================================

# Farben fuer Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # Keine Farbe

echo -e "${CYAN}Produktions-Build - Propositional Logic Trainer${NC}"
echo ""

# Pfad zum Repository-Root (relativ zum Script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Pruefe ob Node.js installiert ist
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js ist nicht installiert!${NC}"
    echo -e "${YELLOW}   Bitte installiere Node.js von https://nodejs.org/${NC}"
    exit 1
fi

# Pruefe ob npm installiert ist
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm ist nicht installiert oder nicht im PATH!${NC}"
    echo -e "${YELLOW}   Bitte installiere Node.js von https://nodejs.org/${NC}"
    exit 1
fi

# Pruefe ob virtuelle Umgebung existiert
if [ ! -d "$REPO_ROOT/.venv" ]; then
    echo -e "${RED}Virtuelle Umgebung nicht gefunden!${NC}"
    echo -e "${YELLOW}   Bitte fuehre zuerst setup.sh aus${NC}"
    exit 1
fi

# Baue Frontend
echo -e "${YELLOW}Baue Frontend...${NC}"
cd "$REPO_ROOT/frontend"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}   Installiere Dependencies...${NC}"
    npm install
fi

echo -e "${YELLOW}   Starte Build-Prozess...${NC}"
npm run build

if [ ! -d "dist" ]; then
    echo -e "${RED}Build fehlgeschlagen!${NC}"
    cd ..
    exit 1
fi

cd "$REPO_ROOT"
echo -e "${GREEN}Frontend gebaut: frontend/dist/${NC}"
echo ""

# Kopiere gebaute Dateien ins Django Static-Verzeichnis
echo -e "${YELLOW}Kopiere statische Dateien...${NC}"
mkdir -p "$REPO_ROOT/staticfiles/frontend"
cp -r "$REPO_ROOT/frontend/dist/"* "$REPO_ROOT/staticfiles/frontend/"
echo -e "${GREEN}Dateien kopiert nach staticfiles/frontend/${NC}"
echo ""

# Aktiviere virtuelle Umgebung und sammle Django Static-Dateien
echo -e "${YELLOW}Django collectstatic...${NC}"
cd "$REPO_ROOT"
source .venv/bin/activate
python manage.py collectstatic --noinput
echo -e "${GREEN}Statische Dateien gesammelt${NC}"
echo ""

# Starte Django-Server mit Waitress
echo -e "${CYAN}Starte Produktions-Server (Waitress)...${NC}"
echo -e "${GREEN}   Server laeuft auf: http://localhost:8000${NC}"
echo ""
echo -e "${YELLOW}Druecke Strg+C zum Stoppen${NC}"
echo ""

# Waitress als Produktions-WSGI-Server
python -m waitress --host=127.0.0.1 --port=8000 logic_trainer.wsgi:application
