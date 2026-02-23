# 🧠 Propositional Logic Trainer

Interaktive Webapp zum Lernen und Üben von aussagenlogischen Inferenzverfahren.

**Technologie-Stack:**
- **Backend:** Django 4.2 + Django REST Framework
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
- **Datenbank:** SQLite (Development) / PostgreSQL (Production)

---

## 📋 Inhaltsverzeichnis

- [Architektur](#architektur)
- [Installation](#installation)
- [Development Workflow](#development-workflow)
- [Production Deployment](#production-deployment)
- [API Dokumentation](#api-dokumentation)
- [Projektstruktur](#projektstruktur)

---

## 🏗️ Architektur

### Zwei Modi: Development vs. Production

```
╔═══════════════════════════════════════════════════════════════╗
║                   DEVELOPMENT MODE                            ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ┌─────────────────────┐         ┌──────────────────────┐   ║
║  │  React Frontend     │   API   │  Django Backend      │   ║
║  │  Port 3000          │ ◄─────► │  Port 8000           │   ║
║  │  (Vite Hot Reload)  │  JSON   │  (REST API + Admin) │   ║
║  └─────────────────────┘         └──────────────────────┘   ║
║         npm run dev              python manage.py runserver  ║
║                                                               ║
║  ✅ Hot Reload - Änderungen sofort sichtbar                  ║
║  ✅ Schnelle Entwicklung                                      ║
║  ❌ 2 Terminal-Fenster nötig                                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════╗
║                   PRODUCTION MODE                             ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║         ┌────────────────────────────────────┐               ║
║         │   Django Server (Port 8000)        │               ║
║         │                                    │               ║
║         │  ┌─ React SPA (statisch)          │               ║
║         │  ├─ REST API (/api/)               │               ║
║         │  ├─ Admin Panel (/admin/)          │               ║
║         │  └─ Static Files                   │               ║
║         └────────────────────────────────────┘               ║
║                 python manage.py runserver                    ║
║                                                               ║
║  ✅ Ein Server - einfaches Deployment                         ║
║  ✅ Realistische Produktionsumgebung                          ║
║  ❌ Nach Frontend-Änderungen: npm run build nötig             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## 💻 Installation

### Voraussetzungen

#### 1. Python 3.11+ (für Backend)
```powershell
# Prüfen ob installiert:
python --version
```

#### 2. Node.js 18+ & npm (für Frontend)

**Was ist Node.js?**  
Node.js ist eine JavaScript-Laufzeitumgebung (ähnlich wie Python selbst).  
Es wird **systemweit** installiert, **NICHT** in Python venv.

**Installation (wähle eine Methode):**

```powershell
# Methode 1: Manueller Download (EMPFOHLEN)
# https://nodejs.org/ (LTS Version)
# Installiere und starte Terminal neu

# Methode 2: Windows Package Manager
winget install OpenJS.NodeJS.LTS

# Methode 3: Chocolatey (falls installiert)
choco install nodejs-lts
```

**Nach Installation prüfen:**
```powershell
node --version   # Sollte v18.x.x oder höher anzeigen
npm --version    # Sollte mit Node.js installiert sein
```

**Wichtig:** Node.js kann **nicht** in Python venv installiert werden - es ist eine eigene Laufzeit!

#### 3. Git (für Version Control)
```powershell
git --version
```

---

### 1️⃣ Repository klonen

```powershell
git clone https://github.com/SinusTangens/Propositional-Logic-Trainer.git
cd Propositional-Logic-Trainer
```

### 2️⃣ Backend Setup

```powershell
# Virtual Environment erstellen und aktivieren
.\setup.sh

# Migrations durchführen
python manage.py migrate

# Superuser erstellen (für /admin/)
python manage.py createsuperuser
```

### 3️⃣ Frontend Setup

```powershell
cd frontend
npm install
cd ..
```

✅ **Installation abgeschlossen!**

---

## 🚀 Development Workflow

### Option 1: Automatisches Startup (EMPFOHLEN)

```powershell
# Startet Frontend + Backend automatisch in separaten Fenstern
.\scripts\start-dev.ps1
```

Öffne dann:
- **Frontend:** http://localhost:3000
- **Backend Admin:** http://localhost:8000/admin/
- **Backend API:** http://localhost:8000/api/

### Option 2: Manuelles Startup

**Terminal 1 - Backend:**
```powershell
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

---

## 🏭 Production Deployment

### Option 1: Automatisches Build & Serve (EMPFOHLEN)

```powershell
# Baut Frontend und startet Django mit integriertem Frontend
.\scripts\start-production.ps1
```

Webapp läuft auf: **http://localhost:8000**

### Option 2: Manuelle Schritte

```powershell
# 1. Frontend bauen
cd frontend
npm run build  # Erstellt frontend/dist/
cd ..

# 2. Django Static Files sammeln
.\.venv\Scripts\Activate.ps1
python manage.py collectstatic --noinput

# 3. Server starten
python manage.py runserver
```

---

## 📡 API Dokumentation

### Base URL
```
http://localhost:8000/api/
```

### Verfügbare Endpoints

**Tasks API**
```typescript
GET    /api/tasks/           // Alle Tasks abrufen
GET    /api/tasks/{id}/      // Einen Task abrufen
POST   /api/tasks/           // Neuen Task erstellen
```

**Users API**
```typescript
GET    /api/users/           // Alle User abrufen
GET    /api/users/{id}/      // Einen User abrufen
GET    /api/users/me/        // Aktueller User
```

**Attempts API**
```typescript
GET    /api/attempts/        // Alle Versuche abrufen
POST   /api/attempts/        // Lösung einreichen

// POST Payload:
{
  "user_id": 1,
  "task_id": 42,
  "solution": {"A": true, "B": false},
  "is_correct": true,
  "feedback": "Korrekt gelöst!"
}
```

### API-Integration im Frontend

```typescript
// src/services/api.ts
import { getTasks, submitAttempt } from './services/api';

// Tasks laden
const { data: tasks, error } = await getTasks();

// Lösung einreichen
const { data: attempt } = await submitAttempt({
  user_id: 1,
  task_id: 42,
  solution: { A: true, B: false },
  is_correct: true,
  feedback: "Richtig!"
});
```

---

## 📁 Projektstruktur

```
propositional-logic-trainer/
├── apps/                      # Django Apps
│   ├── users/                # Benutzer & Authentifizierung
│   │   ├── models.py        # User, Attempt Models
│   │   └── serializers.py   # DRF Serializers
│   ├── generate_tasks/       # Task-Generierung
│   │   ├── models.py        # Task Model
│   │   └── serializers.py
│   ├── solve_tasks/          # Lösungsalgorithmen
│   └── feedback/             # Feedback-Engine
│
├── core/                      # Shared Utilities (Non-Django)
│   ├── logic_engine/
│   │   ├── solver/          # MarginalSolver, BooleanTable
│   │   └── feedback/        # FeedbackEngine
│   └── task_generator/      # Task-Generator
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── components/      # UI Components
│   │   ├── pages/           # Seiten (Lernpfad, Account, etc.)
│   │   ├── services/        # API Integration (api.ts)
│   │   ├── App.tsx          # Hauptkomponente + Routing
│   │   └── main.tsx         # Entry Point
│   ├── package.json
│   └── vite.config.ts
│
├── logic_trainer/             # Django Projekt-Konfiguration
│   ├── settings.py          # Django Settings
│   ├── urls.py              # URL Routing
│   └── wsgi.py
│
├── scripts/                   # Startup-Skripte
│   ├── start-dev.ps1        # Development Mode
│   └── start-production.ps1 # Production Mode
│
├── manage.py                  # Django CLI
├── requirements.txt           # Python Dependencies
├── pyproject.toml            # Package Metadata
└── README.md                 # Diese Datei
```

---

## 🔧 Häufige Befehle

### Django

```powershell
# Server starten
python manage.py runserver

# Neue Migration erstellen
python manage.py makemigrations

# Migration anwenden
python manage.py migrate

# Django Shell öffnen
python manage.py shell

# Superuser erstellen
python manage.py createsuperuser

# Tests ausführen
pytest
```

### Frontend

```powershell
cd frontend

# Dev Server starten
npm run dev

# Production Build
npm run build

# Lint Code
npm run lint

# Dependencies aktualisieren
npm update
```

---

## 🐛 Troubleshooting

### "npm" nicht gefunden
```powershell
# Node.js installieren von https://nodejs.org/
# Terminal neu starten nach Installation
where.exe npm  # Sollte Pfad anzeigen
```

**Hinweis:** Node.js kann **nicht** in Python venv (`.venv/`) installiert werden!  
Es ist eine eigene Laufzeitumgebung und muss systemweit installiert werden.

### Kann ich Node.js in requirements.txt / pyproject.toml packen?
**Nein!** Diese Dateien sind nur für Python-Pakete (pip).  
Node.js ist eine separate Laufzeit (wie Python selbst) und muss separat installiert werden.

### Port bereits belegt
```powershell
# Backend auf anderem Port
python manage.py runserver 8001

# Frontend Port ändern in vite.config.ts
# server: { port: 3001 }
```

### CORS Fehler
```python
# logic_trainer/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",  # Falls geändert
]
```

### Frontend findet Backend nicht
```typescript
// frontend/.env
VITE_API_URL=http://localhost:8000/api
```

### Static Files nicht gefunden
```powershell
# Static Files sammeln
python manage.py collectstatic --noinput

# Development Mode: static files werden automatisch serviert
```

---

## 📚 Weiterführende Dokumentation

- **Django:** https://docs.djangoproject.com/
- **Django REST Framework:** https://www.django-rest-framework.org/
- **React:** https://react.dev/
- **Vite:** https://vitejs.dev/
- **Tailwind CSS:** https://tailwindcss.com/

---

## 📝 License

[Siehe LICENSE Datei]

---

## 👥 Kontakt

**Hochschule Karlsruhe – Technik und Wirtschaft**
- Moltkestraße 30, 76133 Karlsruhe
- Tel: +49 721 925-0
- E-Mail: info@h-ka.de
