#!/bin/bash
# =============================================================================
# Entwicklungs-Startskript - Propositional Logic Trainer
# =============================================================================
# Startet Frontend (React) und Backend (Django) parallel
#
# Verwendung: ./scripts/start-dev.sh
# =============================================================================

# Farben fuer Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # Keine Farbe

echo -e "${CYAN}Starte Propositional Logic Trainer...${NC}"
echo ""

# Pfad zum Repository-Root (relativ zum Script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Pruefe ob Node.js installiert ist
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js ist nicht installiert!${NC}"
    echo -e "${YELLOW}   Bitte installiere Node.js von https://nodejs.org/${NC}"
    echo ""
    exit 1
fi

# Pruefe ob npm installiert ist
if ! command -v npm &> /dev/null; then
    echo -e "${RED}npm ist nicht installiert oder nicht im PATH!${NC}"
    echo -e "${YELLOW}   Bitte installiere Node.js von https://nodejs.org/${NC}"
    echo ""
    exit 1
fi

# Pruefe ob virtuelle Python-Umgebung existiert
if [ ! -d "$REPO_ROOT/.venv" ]; then
    echo -e "${RED}Virtuelle Umgebung nicht gefunden!${NC}"
    echo -e "${YELLOW}   Bitte fuehre zuerst setup.sh aus${NC}"
    echo ""
    exit 1
fi

# Pruefe ob node_modules existiert, falls nicht npm install ausfuehren
if [ ! -d "$REPO_ROOT/frontend/node_modules" ]; then
    echo -e "${YELLOW}Installiere Frontend-Dependencies...${NC}"
    cd "$REPO_ROOT/frontend"
    npm install
    cd "$REPO_ROOT"
    echo -e "${GREEN}Frontend-Dependencies installiert${NC}"
    echo ""
fi

echo -e "${CYAN}Starte beide Services:${NC}"
echo -e "${GREEN}   Frontend: http://localhost:5173${NC}"
echo -e "${GREEN}   Backend:  http://localhost:8000${NC}"
echo -e "${GREEN}   API:      http://localhost:8000/api/${NC}"
echo -e "${GREEN}   Admin:    http://localhost:8000/admin/${NC}"
echo ""
echo -e "${YELLOW}Druecke Strg+C zum Stoppen beider Services${NC}"
echo ""

# Cleanup-Funktion fuer sauberes Beenden
cleanup() {
    echo ""
    echo -e "${YELLOW}Stoppe Services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    wait $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}Services gestoppt${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Aktiviere virtuelle Umgebung und starte Backend
cd "$REPO_ROOT"
echo -e "${CYAN}Starte Backend...${NC}"
source .venv/bin/activate
python manage.py runserver &
BACKEND_PID=$!

# Warte kurz, damit Backend startet
sleep 2

# Starte Frontend
echo -e "${CYAN}Starte Frontend...${NC}"
cd "$REPO_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}Services gestartet!${NC}"
echo -e "${CYAN}   Oeffne http://localhost:5173 im Browser${NC}"
echo ""

# Warte auf beide Prozesse
wait $BACKEND_PID $FRONTEND_PID
