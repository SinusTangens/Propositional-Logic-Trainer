# 🧠 Propositional Logic Trainer

Eine interaktive Web-Anwendung zum Erlernen und Üben von aussagenlogischen Inferenzverfahren.

## Beschreibung

Das Ziel dieser Arbeit ist die Konzeption und Umsetzung einer **digitalen Übungsplattform**, die Studierende beim Erlernen des logischen Schließens im Bereich der Aussagenlogik unterstützt. 

Die Anwendung bietet:
- **Automatisierte Aufgabengenerierung** - Unbegrenzte Übungsmöglichkeiten
- **Sofortige Auswertung** - Direktes Feedback zu Lösungsversuchen
- **Adaptive Schwierigkeit** - Anpassung an das individuelle Lernverhalten
- **Lernfortschritttracking** - Sichtbarer Fortschritt zur Motivation
- **Verschiedene Lösungsverfahren** - Unit Propagation, Case Split und mehr

---

## 📋 Inhaltsverzeichnis

- [Technologien](#-technologien)
- [Projekt-Setup](#-projekt-setup)
- [Server starten](#-server-starten)
  - [Development Mode](#development-mode)
  - [Production Mode](#production-mode)
- [Architektur](#-architektur)
- [Django Befehle](#-wichtige-django-befehle)
- [Projektstruktur](#-projektstruktur)
- [Weiterführende Dokumentation](#-weiterführende-dokumentation)
- [License](#-license)
- [Kontakt](#-kontakt)

---

## 🛠️ Technologien

### Backend
| Technologie | Version | Beschreibung |
|-------------|---------|--------------|
| Python | 3.11+ | Programmiersprache |
| Django | 5.2 | Web-Framework |
| Django REST Framework | 3.16 | REST API |
| SymPy | 1.12+ | Symbolische Mathematik |
| Waitress | 3.0+ | WSGI Server (Windows) |
| Whitenoise | 6.6+ | Static File Serving |
| pytest | 8.0+ | Testing Framework |

### Frontend
| Technologie | Version | Beschreibung |
|-------------|---------|--------------|
| React | 18.3 | UI Framework |
| TypeScript | 5.7 | Type-safe JavaScript |
| Vite | 6.3 | Build Tool & Dev Server |
| Tailwind CSS | 4.0 | Utility-first CSS |
| Radix UI | - | Accessible Components |
| Lucide React | - | Icon Library |

### Datenbank
- **SQLite** - Development & Production (für Thesis ausreichend)

---

## 💻 Projekt-Setup

### Voraussetzungen

#### 1. Python 3.11+
```powershell
python --version
```

#### 2. Node.js 18+ & npm
Node.js ist eine separate Laufzeitumgebung (nicht in Python venv installierbar).

```powershell
# Installation: https://nodejs.org/ (LTS Version)
# Nach Installation:
node --version
npm --version
```

#### 3. Git
```powershell
git --version
```

### Installation

```powershell
# 1. Repository klonen
git clone https://github.com/SinusTangens/Propositional-Logic-Trainer.git
cd Propositional-Logic-Trainer

# 2. Python Virtual Environment erstellen
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Python Dependencies installieren
pip install -r requirements.txt

# 4. Django Migrationen durchführen
python manage.py migrate

# 5. Superuser erstellen (für Admin-Panel)
python manage.py createsuperuser

# 6. Frontend Dependencies installieren
cd frontend
npm install
cd ..
```

✅ **Installation abgeschlossen!**

---

## 🚀 Server starten

### Development Mode

**Empfohlen für Entwicklung** - Hot Reload, schnelle Iteration.

#### Mit Script (empfohlen)
```powershell
.\scripts\start-dev.ps1
```

#### Manuell (2 Terminals)

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

**URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/

---

### Production Mode

**Empfohlen für Präsentation/Demo** - Ein Server, professionell.

#### Mit Script (empfohlen)
```powershell
.\scripts\start-production.ps1
```

#### Manuell
```powershell
# 1. Virtual Environment aktivieren
.\.venv\Scripts\Activate.ps1

# 2. Frontend bauen
cd frontend
npm run build
cd ..

# 3. Static Files sammeln
python manage.py collectstatic --noinput

# 4. Production Server starten
python -c "from waitress import serve; from logic_trainer.wsgi import application; print('Server: http://localhost:8000'); serve(application, host='0.0.0.0', port=8000)"
```

**URL:** http://localhost:8000 (alles über einen Port)

---

## 🏗️ Architektur

### Development Mode
```
┌─────────────────────────────────────────────────────────────────┐
│                      DEVELOPMENT MODE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐         ┌──────────────────────┐      │
│  │  React Frontend     │   API   │  Django Backend      │      │
│  │  Port 5173          │ ◄─────► │  Port 8000           │      │
│  │  (Vite Hot Reload)  │  JSON   │  (REST API + Admin)  │      │
│  └─────────────────────┘         └──────────────────────┘      │
│       npm run dev                 python manage.py runserver    │
│                                                                 │
│  ✅ Hot Reload - Änderungen sofort sichtbar                     │
│  ✅ Schnelle Entwicklung                                        │
│  ❌ 2 Terminal-Fenster nötig                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Production Mode
```
┌─────────────────────────────────────────────────────────────────┐
│                      PRODUCTION MODE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│         ┌────────────────────────────────────┐                  │
│         │ Waitress/Django Server (Port 8000) │                  │
│         │                                    │                  │
│         │  ┌─ React SPA (statisch via        │                  │
│         │  │  Whitenoise)                    │                  │
│         │  ├─ REST API (/api/)               │                  │
│         │  ├─ Admin Panel (/admin/)          │                  │
│         │  └─ Static Files (/static/)        │                  │
│         └────────────────────────────────────┘                  │
│                                                                 │
│  ✅ Ein Server - einfaches Deployment                           │
│  ✅ Professionell für Präsentationen                            │
│  ❌ Nach Frontend-Änderungen: Build nötig                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Build-Workflow
```
frontend/src/     →    npm run build    →    frontend/dist/
                                                   │
                                                   ▼
                       collectstatic     →    staticfiles/
                                                   │
                                                   ▼
                       Whitenoise serviert statische Dateien
```

---

## 🔧 Wichtige Django Befehle

### Server & Migrations
```powershell
# Development Server starten
python manage.py runserver

# Neue Migration erstellen (nach Model-Änderungen)
python manage.py makemigrations

# Migrationen anwenden
python manage.py migrate

# Static Files sammeln (für Production)
python manage.py collectstatic --noinput
```

### Admin & Debugging
```powershell
# Superuser erstellen
python manage.py createsuperuser

# Django Shell öffnen
python manage.py shell

# Alle URLs anzeigen
python manage.py show_urls
```

### Aufgaben-Generierung
```powershell
# Task-Pool Status prüfen
python manage.py prefill_tasks --status

# Tasks vorab generieren
python manage.py prefill_tasks --type UNIT_PROPAGATION --level 1 --count 10
python manage.py prefill_tasks --type CASE_SPLIT --level 2 --count 5
```

### Tests
```powershell
# Django API Tests
python manage.py test apps

# Core Logic Tests (pytest)
pytest core/tests/

# Alle Tests
pytest
```

### Frontend Befehle
```powershell
cd frontend

# Development Server
npm run dev

# Production Build
npm run build

# Linting
npm run lint
```

---

## 📁 Projektstruktur

```
prop-logic-trainer/
│
├── apps/                          # Django Apps (API Layer)
│   ├── users/                     # Benutzer & Authentifizierung
│   │   ├── models.py             # User, Attempt Models
│   │   ├── views.py              # REST ViewSets
│   │   └── serializers.py        # DRF Serializers
│   ├── generate_tasks/            # Task-Generierung API
│   ├── solve_tasks/               # Lösungsverarbeitung API
│   └── feedback/                  # Feedback-Engine API
│
├── core/                          # Business Logic (Non-Django)
│   ├── logic_engine/
│   │   ├── solver/               # Bucket Elimination, SymPy
│   │   └── feedback/             # FeedbackEngine
│   ├── task_generator/           # Aufgaben-Generator
│   └── tests/                    # pytest Tests
│
├── frontend/                      # React SPA
│   ├── src/
│   │   ├── components/           # UI Components
│   │   ├── pages/                # Seiten (Lernpfad, Account, etc.)
│   │   ├── services/             # API Integration
│   │   ├── contexts/             # React Context (State)
│   │   └── logic_visualizer/     # Formel-Visualisierung
│   ├── package.json
│   └── vite.config.ts
│
├── logic_trainer/                 # Django Konfiguration
│   ├── settings.py               # Django Settings
│   └── urls.py                   # URL Routing
│
├── scripts/                       # Startup-Skripte
│   ├── start-dev.ps1             # Development Mode
│   └── start-production.ps1      # Production Mode
│
├── docs/                          # Dokumentation
│   ├── research/                 # Forschungsunterlagen
│   ├── architecture/             # Architektur-Diagramme
│   └── thesis/                   # Thesis-Materialien
│
├── examples/                      # Beispieldaten
│
├── manage.py                      # Django CLI
├── requirements.txt               # Python Dependencies
├── pyproject.toml                 # Package Metadata
├── .gitignore                     # Git Ignore Rules
└── README.md                      # Diese Datei
```

---

## 📚 Weiterführende Dokumentation

### Framework-Dokumentation
- **Django:** https://docs.djangoproject.com/
- **Django REST Framework:** https://www.django-rest-framework.org/
- **React:** https://react.dev/
- **Vite:** https://vite.dev/
- **Tailwind CSS:** https://tailwindcss.com/

### API Endpunkte

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/tasks/` | GET | Alle Tasks abrufen |
| `/api/tasks/{id}/` | GET | Einen Task abrufen |
| `/api/tasks/next/` | GET | Nächste adaptive Aufgabe |
| `/api/users/` | GET | Alle User abrufen |
| `/api/users/me/` | GET | Aktueller User |
| `/api/attempts/` | POST | Lösung einreichen |

### Troubleshooting

**Port bereits belegt:**
```powershell
python manage.py runserver 8001
```

**CORS Fehler:** Prüfe `CORS_ALLOWED_ORIGINS` in `logic_trainer/settings.py`

**Static Files nicht gefunden:** 
```powershell
python manage.py collectstatic --noinput
```

**Module not found:**
```powershell
# Python
pip install -r requirements.txt

# Node.js
cd frontend && npm install
```

---

## 📝 License

Dieses Projekt ist im Rahmen einer Bachelorarbeit an der Hochschule Karlsruhe entstanden.

---

## 👥 Kontakt

**Hochschule Karlsruhe – Technik und Wirtschaft**

📍 Moltkestraße 30, 76133 Karlsruhe  
📞 +49 721 925-0  
📧 info@h-ka.de  
🌐 https://www.h-ka.de
