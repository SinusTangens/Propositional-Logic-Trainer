# Propositional Logic Trainer - Start Scripts

Dieses Verzeichnis enthält PowerShell-Skripte zum einfachen Starten der Anwendung.

## Development Mode (Entwicklung)

Startet Frontend und Backend **getrennt** in zwei Terminals:

```powershell
.\scripts\start-dev.ps1
```

- **Frontend:** http://localhost:3000 (Vite Dev Server mit Hot Reload)
- **Backend:** http://localhost:8000 (Django API)
- **Vorteil:** Änderungen sofort sichtbar, schnelle Entwicklung
- **Nachteil:** 2 Terminal-Fenster nötig

## Production Mode (Produktion)

Baut das Frontend und serviert alles über Django auf **einem Port**:

```powershell
.\scripts\start-production.ps1
```

- **Alles:** http://localhost:8000 (Django serviert Frontend + Backend)
- **Vorteil:** Nur ein Server, realistischer für Deployment
- **Nachteil:** Nach Frontend-Änderungen muss neu gebaut werden

## Was ist der Unterschied?

### Development (start-dev.ps1)
```
┌─────────────────┐         ┌──────────────────┐
│ React Frontend  │  API    │ Django Backend   │
│ Port 3000       │ ←────→  │ Port 8000        │
│ (Vite)          │         │ (Python)         │
└─────────────────┘         └──────────────────┘
     Fenster 1                   Fenster 2
```

### Production (start-production.ps1)
```
┌────────────────────────────────────────┐
│        Django Server (Port 8000)       │
│  ├─ API Endpoints (/api/)              │
│  ├─ Admin Interface (/admin/)          │
│  └─ React Frontend (statische Files)   │
└────────────────────────────────────────┘
            Ein Fenster
```

## Erstmaliges Setup

Falls noch nicht geschehen:

```powershell
# 1. Python Environment
.\setup.sh

# 2. Node.js Dependencies (nur einmalig)
cd frontend
npm install
cd ..

# 3. Django Migrations
.\.venv\Scripts\Activate.ps1
python manage.py migrate

# 4. Superuser erstellen
python manage.py createsuperuser
```

## Troubleshooting

### "Node.js ist nicht installiert"
- Download: https://nodejs.org/ (LTS Version)
- Nach Installation Terminal neu starten

### "Virtual Environment nicht gefunden"
```powershell
.\setup.sh
```

### Port bereits belegt
```powershell
# Backend auf anderem Port starten
python manage.py runserver 8001

# Frontend Port ändern in vite.config.ts:
# server: { port: 3001 }
```
