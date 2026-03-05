# 🧠 Propositional Logic Trainer

Eine interaktive Web-Anwendung zum Erlernen und Üben von aussagenlogischen Inferenzverfahren.

## Beschreibung

Das Ziel dieser Arbeit ist die Konzeption und Umsetzung einer **digitalen Übungsplattform**, die Studierende beim Erlernen des logischen Schließens im Bereich der Aussagenlogik unterstützt. 

Die Anwendung bietet:
- **Automatisierte Aufgabengenerierung** - Unbegrenzte Übungsmöglichkeiten
- **Sofortige Auswertung** - Direktes Feedback zu Lösungsversuchen
- **Levelsystem** - Breit gefächerte Schwierigkeitsgrade für schrittweises Lernen
- **Lernfortschritttracking** - Sichtbarer Fortschritt zur Motivation
- **Verschiedene Lösungsverfahren** - Unit Propagation, Case Split

---

## 📋 Inhaltsverzeichnis

- [Technologien](#-technologien)
- [Projekt-Setup](#-projekt-setup)
- [Server starten](#-server-starten)
  - [Development Mode](#development-mode)
  - [Production Mode](#production-mode)
- [Architektur](#-architektur)
- [Django Befehle](#-django-befehle)
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
- **SQLite** - Development & Production 

---

## 💻 Projekt-Setup


**1. Repository clonen**
```bash
git clone https://github.com/SinusTangens/Propositional-Logic-Trainer.git
cd Propositional-Logic-Trainer
```

**2. Node.js installieren** (falls noch nicht vorhanden):  
→ https://nodejs.org/ (LTS Version)

**3. Setup-Skript ausführen:**

| Betriebssystem | Befehl |
|----------------|--------|
| Windows (PowerShell) | `.\scripts\setup.ps1` |
| macOS / Linux / Windows (Git Bash) | `bash scripts/setup.sh` |

> **Hinweis Windows:** Falls das Skript blockiert wird, einmalig ausführen:  
> `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
>
> **Hinweis macOS/Linux:** Die Shell-Skripte setzen automatisch ihre Ausführungsrechte. Beim ersten Aufruf `bash scripts/setup.sh` verwenden, danach funktioniert `./scripts/setup.sh` direkt.

Das Setup-Skript:
- Installiert Python 3.11 via [uv](https://docs.astral.sh/uv/)
- Erstellt eine virtuelle Umgebung (`.venv`)
- Installiert alle Python-Dependencies
- Führt Datenbank-Migrationen aus


**4. Virtuelle Umgebung aktivieren**

Die virtuelle Umgebung (`.venv`) wird in den meisten IDEs automatisch erkannt:

- **VS Code / PyCharm**: Öffnen Sie ein neues Terminal – die venv wird automatisch aktiviert
- **Andere Editoren / externe Terminals**: Manuell aktivieren:

| Betriebssystem | Befehl |
|---|---|
| Windows (PowerShell) | `.\venv\Scripts\Activate.ps1` |
| macOS / Linux / Git Bash | `source .venv/bin/activate` |

Nach erfolgreicher Aktivierung erscheint `(.venv)` am Anfang der Kommandozeile.

> **Hinweis:** Je nach Setup kann auch der Projektname angezeigt werden, z.B. `(prop-logic-trainer)` statt `(.venv)`. 


**5. Aufgaben vorgenerieren (empfohlen)**

Komplexere Aufgaben (insbesondere CASE_SPLIT) können bei der ersten Anfrage lange zum Generieren brauchen. Es wird empfohlen, die Datenbank vor der Nutzung mit Aufgaben zu füllen:

```bash
# Task-Pool vorab generieren 
python manage.py prefill_tasks
```

Das ist **optional**, aber **empfohlen**, damit die App später responsiv läuft.

---

## 🚀 Server starten

Die Anwendung kann in zwei Modi gestartet werden.

### Development Mode

**Empfohlen für Entwicklung** - Hot Reload, schnelle Iteration.

#### Mit Script (empfohlen)

| Betriebssystem | Befehl |
|----------------|--------|
| Windows (PowerShell) | `.\scripts\start-dev.ps1` |
| macOS / Linux | `./scripts/start-dev.sh` |


#### Manuell

**Terminal 1 - Backend:**
```bash
# venv muss aktiviert sein!
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
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

| Betriebssystem | Befehl |
|----------------|--------|
| Windows (PowerShell) | `.\scripts\start-production.ps1` |
| macOS / Linux | `./scripts/start-production.sh` |

#### Manuell
```bash
# venv muss aktiviert sein!

# 1. Frontend bauen
cd frontend
npm run build
cd ..

# 2. Static Files sammeln
python manage.py collectstatic --noinput

# 3. Production Server starten
python -m waitress --host=127.0.0.1 --port=8000 logic_trainer.wsgi:application
```

**URL:** http://localhost:8000 (alles über einen Port)

---

## 🏗️ Architektur

> **Detaillierte Dokumentation:** Siehe [docs/architecture/SOFTWAREARCHITEKTUR.md](docs/architecture/SOFTWAREARCHITEKTUR.md) für die vollständige technische Architektur inkl. Schichtenmodell, Datenmodell, Core Logic Engine und API-Dokumentation.

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

---

## 🔧 Django Befehle

```powershell

# Listet alle Befehle der Django CLI auf 
python manage.py
```


### Server & Migrations
```powershell

#Deployment Server starten
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
# Superuser erstellen (um das Admin Panel zu nutzen)
python manage.py createsuperuser

# Django Shell öffnen
python manage.py shell

# Alle URLs anzeigen
python manage.py show_urls
```

### Vorgenerierung Aufgaben

Generiert Aufgaben und schreibt sie in die Datenbank (200 pro Aufgabentyp-Level).
Standardmäßig **parallel** auf alle CPU-Kerne verteilt.

```powershell
# Generiert für alle Aufgabentypen und Level (parallel)
python manage.py prefill_tasks

# Sequenziell ausführen (weniger Ressourcen)
python manage.py prefill_tasks --sequential

# Mit begrenzter Worker-Anzahl
python manage.py prefill_tasks --workers 4

# Nur bestimmter Aufgabentyp und Level
python manage.py prefill_tasks --type CASE_SPLIT --level 2

# Status anzeigen
python manage.py prefill_tasks --status
```

### Tests
```powershell
# Django API Tests
python manage.py test apps

# Core Logic Tests (pytest)
pytest core/tests/

# Workflow-Integrationtest
python core/tests/workflow_test.py


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
│   └── feedback/                  # Feedback-Engine API (für spätere Feedbackmechanismen)
│
├── core/                          # Business Logic (Non-Django)
│   ├── logic_engine/
│   │   ├── solver/               # Bucket Elimination Solver
│   │   └── feedback/             # FeedbackEngine
│   ├── task_generator/           # Aufgaben-Generator
│   └── tests/                    # pytest Tests
│
├── frontend/                      # React SPA
│   ├── src/
│   │   ├── components/           # UI Components
│   │   │   └── ui/               # Radix UI Wrapper
│   │   ├── pages/                # Seiten (Lernpfad, Account, etc.)
│   │   ├── services/             # API Integration
│   │   ├── contexts/             # React Context (State)
│   │   ├── lib/                  # Utility-Funktionen
│   │   ├── styles/               # CSS Styles
│   │   └── assets/               # Statische Assets
│   ├── package.json
│   └── vite.config.ts
│
├── logic_trainer/                 # Django Konfiguration
│   ├── settings.py               # Django Settings
│   ├── urls.py                   # URL Routing
│   ├── wsgi.py                   # WSGI Entry Point
│   └── asgi.py                   # ASGI Entry Point
│
├── scripts/                       # Startup-Skripte
│   ├── setup.ps1                 # Setup (Windows PowerShell)
│   ├── setup.sh                  # Setup (macOS/Linux/Git Bash)
│   ├── start-dev.ps1             # Development Mode (Windows)
│   ├── start-dev.sh              # Development Mode (macOS/Linux)
│   ├── start-production.ps1      # Production Mode (Windows)
│   └── start-production.sh       # Production Mode (macOS/Linux)
│
├── docs/                          # Dokumentation
│   ├── research/                 # Forschungsunterlagen
│   ├── architecture/             # Architektur-Diagramme
│   └── thesis/                   # Thesis-Materialien
│
├── examples/                      # Beispieldaten
│   ├── sample_tasks/             # Beispielaufgaben
│   └── solution_walkthroughs/    # Lösungswege
│
├── staticfiles/                   # Gesammelte Static Files (Production)
│
├── manage.py                      # Django CLI
├── requirements.txt               # Python Dependencies
├── pyproject.toml                 # Package Metadata
├── .gitignore                     # Git Ignore Rules
├── .gitattributes                 # Git Zeilenenden-Konfiguration
├── .python-version                # Python Version (für uv/pyenv)
├── LICENSE                        # Lizenz
└── README.md                      # Diese Datei
```

---

## 📚 Weiterführende Dokumentation


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
### Framework-Dokumentation
- **Django:** https://docs.djangoproject.com/
- **Django REST Framework:** https://www.django-rest-framework.org/
- **React:** https://react.dev/
- **Vite:** https://vite.dev/
- **Tailwind CSS:** https://tailwindcss.com/

---

## 👥 Kontakt

**Autor:** Sinan Kammerer  
📧 kasi1021@h-ka.de

**Betreuung:** Prof. Dr. Reimar Hofmann  
📧 hore0001@h-ka.de

---

**Hochschule Karlsruhe – Technik und Wirtschaft**  
📍 Moltkestraße 30, 76133 Karlsruhe  
🌐 https://www.h-ka.de

