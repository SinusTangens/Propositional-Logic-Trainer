# Softwarearchitektur – Propositional Logic Trainer

Dieses Dokument beschreibt die technische Architektur der Anwendung für Außenstehende (insbesondere Prüfer). Es erklärt die Struktur, Verantwortlichkeiten und Zusammenhänge aller Komponenten.

---

## Inhaltsverzeichnis

1. [Systemübersicht](#1-systemübersicht)
2. [Schichtenarchitektur](#2-schichtenarchitektur)
3. [Backend-Struktur (Django)](#3-backend-struktur-django)
4. [Core Logic Engine](#4-core-logic-engine)
5. [Frontend-Struktur (React)](#5-frontend-struktur-react)
6. [Datenmodell](#6-datenmodell)
7. [Aufgabengenerierung und -verwaltung](#7-aufgabengenerierung-und--verwaltung)
8. [Lösungsverifikation und Feedback](#8-lösungsverifikation-und-feedback)
9. [API-Kommunikation](#9-api-kommunikation)
10. [Konfigurationsdateien](#10-konfigurationsdateien)

---

## 1. Systemübersicht

Der **Propositional Logic Trainer** ist eine Web-Anwendung zum Erlernen aussagenlogischer Inferenzverfahren. Die Architektur folgt dem **Client-Server-Modell** mit klarer Trennung zwischen:

- **Frontend**: React Single-Page-Application (SPA) für die Benutzerinteraktion
- **Backend**: Django REST API für Geschäftslogik und Datenpersistenz
- **Core**: Python-Module für die mathematische Logik (unabhängig von Django)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          GESAMTARCHITEKTUR                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────┐                    ┌──────────────────────────┐  │
│   │  React Frontend  │  ◄── REST API ──►  │    Django Backend       │  │
│   │  (TypeScript)    │       (JSON)        │    (Python)             │  │
│   │                  │                     │                         │  │
│   │  - UI Components │                     │  ┌─────────────────────┐│  │
│   │  - State Mgmt    │                     │  │   Django Apps       ││  │
│   │  - API Service   │                     │  │   (API Layer)       ││  │
│   └──────────────────┘                     │  └─────────────────────┘│  │
│                                            │            │            │  │
│                                            │            ▼            │  │
│                                            │  ┌─────────────────────┐│  │
│                                            │  │   Core Logic        ││  │
│                                            │  │   (Business Logic)  ││  │
│                                            │  └─────────────────────┘│  │
│                                            │            │            │  │
│                                            │            ▼            │  │
│                                            │  ┌─────────────────────┐│  │
│                                            │  │   SQLite Database   ││  │
│                                            │  └─────────────────────┘│  │
│                                            └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Schichtenarchitektur

Die Anwendung folgt einer **3-Schichten-Architektur** mit zusätzlicher Trennung der Geschäftslogik:

| Schicht | Technologie | Verantwortlichkeit |
|---------|-------------|-------------------|
| **Präsentation** | React + TypeScript | UI, Benutzerinteraktion |
| **API** | Django REST Framework | HTTP-Endpunkte, Serialisierung, Authentifizierung |
| **Geschäftslogik** | Python (core/) | Aufgabengenerierung, Solver, Feedback |
| **Persistenz** | Django ORM + SQLite | Datenhaltung, Models |

### Warum diese Trennung?

- **Core ist Django-unabhängig**: Die mathematische Logik kann ohne Web-Framework getestet werden
- **API ist austauschbar**: Die REST-Schicht könnte durch GraphQL ersetzt werden
- **Frontend ist entkoppelt**: Könnte durch eine Mobile-App ersetzt werden

---

## 3. Backend-Struktur (Django)

### 3.1 Verzeichnis `logic_trainer/`

Django-Projektkonfiguration:

| Datei | Funktion |
|-------|----------|
| `settings.py` | Zentrale Django-Konfiguration (Datenbank, Middleware, CORS, etc.) |
| `urls.py` | Haupt-URL-Routing (delegiert an App-URLs) |
| `wsgi.py` | WSGI Entry Point für Production Server (Waitress) |
| `asgi.py` | ASGI Entry Point (für zukünftige WebSocket-Unterstützung) |

### 3.2 Verzeichnis `apps/`

Enthält die Django-Apps, die die REST API bereitstellen:

#### `apps/generate_tasks/` – Aufgabenverwaltung

| Datei | Funktion |
|-------|----------|
| `models.py` | **Task-Model**: Speichert generierte Aufgaben (Prämissen, Variablen, Level) |
| `views.py` | **TaskViewSet**: CRUD-Operationen + `/generate/` + `/pool_status/` |
| `serializers.py` | JSON-Serialisierung der Task-Objekte |
| `services.py` | **TaskPreGenerationService**: Singleton für Task-Pool-Management |
| `signals.py` | Django Signal: Triggert Nachgenerierung nach Attempt-Erstellung |
| `urls.py` | URL-Routing für `/api/tasks/` |
| `management/commands/` | Django CLI Command `prefill_tasks` |

**Schlüsselkonzept – Pre-Generation:**  
Tasks werden vorab generiert und in der Datenbank gespeichert. Wenn ein Benutzer eine Aufgabe anfordert, wird eine bereits generierte Task aus dem Pool entnommen. Dies vermeidet lange Wartezeiten bei komplexen Aufgabentypen (Case Split kann Sekunden dauern).

#### `apps/users/` – Benutzerverwaltung

| Datei | Funktion |
|-------|----------|
| `models.py` | **User** (erweiterter Django-User), **UserProgress** (Fortschritt pro Level), **Attempt** (Lösungsversuche) |
| `views.py` | Auth-Endpoints (Register, Login, Logout), UserViewSet, Avatar-Endpoints |
| `serializers.py` | Serialisierung für User, Progress, Attempt |
| `urls.py` | URL-Routing für `/api/auth/` und `/api/users/` |

**Schlüsselkonzept – Level-Tracking:**  
`UserProgress` speichert den Fortschritt pro Aufgabentyp und Level. Erst nach X aufeinanderfolgenden korrekten Antworten wird das nächste Level freigeschaltet (konfigurierbar in `LEVEL_CONFIG`).

#### `apps/solve_tasks/` – Lösungsverarbeitung

| Datei | Funktion |
|-------|----------|
| `models.py` | **SolutionCache**: Speichert berechnete Lösungen für Performance |
| `views.py` | **SolveTaskView**: Nimmt Antworten entgegen, vergleicht mit Lösung |
|            | **GetFeedbackView**: Generiert detailliertes Feedback |
|            | **GetSolutionView**: Gibt komplette Lösung zurück |
| `urls.py` | URL-Routing für `/api/solve/`, `/api/feedback/`, `/api/solution/` |

**Schlüsselkonzept – Caching:**  
Da das Lösen einer Aufgabe rechenintensiv ist (Bucket Elimination), wird das Ergebnis gecacht. Bei wiederholten Anfragen wird der Cache verwendet.

#### `apps/feedback/` – (Reserviert für zukünftige Erweiterungen)

Aktuell leer. Geplant für erweiterte Feedback-Mechanismen.

---

## 4. Core Logic Engine

Das `core/`-Verzeichnis enthält die mathematische Kernlogik, **komplett unabhängig von Django**:

### 4.1 `core/task_generator/`

| Datei | Funktion |
|-------|----------|
| `Task.py` | **Datenklassen und Konfiguration** |
|           | - `TaskType`: Enum für Aufgabentypen (DIRECT_INFERENCE, CASE_SPLIT) |
|           | - `Task`: Dataclass für eine Aufgabe |
|           | - `DifficultySpec`: Schwierigkeitsparameter |
|           | - `DIFFICULTY_CONFIG`: Zentrale Konfiguration aller Level |
| `generate_tasks.py` | **TaskGenerator**: Generiert zufällige, lösbare Aufgaben |

**Algorithmus der Aufgabengenerierung:**

```
1. Wähle Variablen (A, B, C, ...) basierend auf Level
2. Generiere zufällige SymPy-Formeln als Prämissen
3. Prüfe ob Aufgabe:
   a) Lösbar ist (mindestens ein Modell existiert)
   b) Eindeutig genug ist (nicht alle Variablen beliebig)
   c) Den Schwierigkeitskriterien entspricht
4. Wiederhole bis gültige Aufgabe gefunden
```

### 4.2 `core/logic_engine/solver/`

| Datei | Funktion |
|-------|----------|
| `BooleanTable.py` | Datenstruktur für Wahrheitstabellen (NumPy-basiert) |
| `MarginalSolver.py` | **BucketElimination**: Implementiert den Shenoy-Shafer Algorithmus |

**Bucket Elimination Algorithmus:**

Der Solver verwendet Variablenelimination, um die Lösbarkeit und eindeutige Belegungen zu bestimmen:

```
Forward Pass (Elimination):
  Für jede Variable v in Eliminationsreihenfolge:
    1. Sammle alle Tabellen, die v enthalten (Bucket)
    2. Kombiniere sie (logisches UND)
    3. Marginalisiere v heraus (logisches ODER über v)
    4. Speichere Ergebnis für Backward Pass

Backward Pass (Bestimmung):
  Für jede Variable v in umgekehrter Reihenfolge:
    1. Lade gespeicherten Bucket
    2. Setze bekannte Werte ein
    3. Prüfe ob v eindeutig bestimmt ist (True/False/None)
```

### 4.3 `core/logic_engine/feedback/`

| Datei | Funktion |
|-------|----------|
| `UserInput.py` | Enum für Benutzereingaben (TRUE, FALSE, UNKNOWN) |
| `FeedbackEngine.py` | Generiert differenziertes Feedback basierend auf Fehlertyp |

**Feedback-Kategorien:**

| Fall | Beschreibung | Reaktion |
|------|-------------|----------|
| Korrekt | Antwort stimmt | Lob |
| Unnötige Annahme | User sagt True/False, aber Unbekannt | Gegenbeispiel generieren |
| Verpasste Schlussfolgerung | User sagt Unbekannt, aber festgelegt | Hinweis auf zwingende Folgerung |
| Falsche Belegung | User sagt True statt False | Korrektur mit Erklärung |

### 4.4 `core/tests/`

| Datei | Funktion |
|-------|----------|
| `bucket_elimination_test.py` | pytest-Tests für den Solver (verifiziert gegen SymPy) |
| `workflow_test.py` | Interaktiver End-to-End Test |

---

## 5. Frontend-Struktur (React)

### 5.1 `frontend/src/`

| Verzeichnis/Datei | Funktion |
|-------------------|----------|
| `main.tsx` | React Entry Point |
| `App.tsx` | Haupt-Komponente, React Router Setup |

### 5.2 `components/`

Wiederverwendbare UI-Komponenten:

| Komponente | Funktion |
|------------|----------|
| `ui/` | Radix UI Primitives (Button, Card, Dialog, etc.) |
| `AvatarEditor.tsx` | Komponente zur Avatar-Anpassung |
| `CelebrationModal.tsx` | Erfolgs-Animation bei Level-Abschluss |
| `SelectionCard.tsx` | Karte für Aufgabentyp-Auswahl |

### 5.3 `pages/`

Seitenkomponenten (entsprechen Routen):

| Seite | Route | Funktion |
|-------|-------|----------|
| `Lernpfad.tsx` | `/` | Übersicht der Aufgabentypen und Level |
| `UnitPropagation.tsx` | `/unit-propagation/:level` | Interaktive Aufgabe (DIRECT_INFERENCE) |
| `CaseSplit.tsx` | `/case-split/:level` | Interaktive Aufgabe (CASE_SPLIT) |
| `Account.tsx` | `/account` | Profil, Statistiken, Avatar |
| `Login.tsx` | `/login` | Anmeldung/Registrierung |
| `Grundlagen.tsx` | `/grundlagen` | Theorie-Seite |
| `FreiesUeben.tsx` | `/freies-ueben` | Übungsmodus ohne Fortschritt |

### 5.4 `services/`

| Datei | Funktion |
|-------|----------|
| `api.ts` | Zentraler API-Service (fetch-Wrapper, CSRF-Handling) |

### 5.5 `contexts/`

React Context für globalen State:

| Context | Funktion |
|---------|----------|
| `AuthContext` | Authentifizierungsstatus, User-Objekt |
| `ProgressContext` | Lernfortschritt des Benutzers |

### 5.6 Weitere Verzeichnisse

| Verzeichnis | Funktion |
|-------------|----------|
| `lib/` | Utility-Funktionen (z.B. `cn()` für Tailwind-Klassen) |
| `styles/` | Globale CSS-Dateien |
| `assets/` | Statische Assets (Bilder, etc.) |

---

## 6. Datenmodell

### Entity-Relationship-Diagramm

```
┌─────────────┐       ┌─────────────┐       ┌─────────────────┐
│    User     │       │    Task     │       │  UserProgress   │
├─────────────┤       ├─────────────┤       ├─────────────────┤
│ id          │       │ id          │       │ id              │
│ username    │       │ task_type   │       │ user_id (FK)    │
│ password    │       │ level       │       │ task_type       │
│ total_solved│       │ premises    │       │ current_level   │
│ current_streak      │ premises_sympy      │ streak_count    │
│ avatar_*    │       │ variables   │       │ is_completed    │
└─────────────┘       │ created_at  │       └─────────────────┘
      │               └─────────────┘              │
      │                     │                      │
      │    ┌────────────────┴──────────────┐      │
      │    │                               │      │
      ▼    ▼                               ▼      │
┌─────────────────┐                ┌──────────────┴───┐
│    Attempt      │                │  SolutionCache   │
├─────────────────┤                ├──────────────────┤
│ id              │                │ id               │
│ user_id (FK)    │                │ task_id          │
│ task_id (FK)    │                │ solver_name      │
│ answers         │                │ result           │
│ is_correct      │                │ created_at       │
│ created_at      │                └──────────────────┘
└─────────────────┘
```

### Modell-Beschreibungen

| Modell | Beschreibung |
|--------|--------------|
| **User** | Erweiterter Django-User mit Statistiken und Avatar-Einstellungen |
| **Task** | Gespeicherte Aufgabe mit Prämissen in zwei Formaten (lesbar + SymPy) |
| **UserProgress** | Fortschritt eines Users pro Aufgabentyp (Level, Streak, Status) |
| **Attempt** | Ein Lösungsversuch eines Users für eine Aufgabe |
| **SolutionCache** | Gecachte Solver-Ergebnisse für Performance |

---

## 7. Aufgabengenerierung und -verwaltung

### 7.1 Generierungspipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUFGABENGENERIERUNG                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │ DIFFICULTY_ │───►│ TaskGenerator│───►│ generierte SymPy-   │ │
│  │ CONFIG      │    │             │    │ Formeln (Prämissen) │ │
│  │ (Task.py)   │    │ (generate_  │    │                     │ │
│  │             │    │ tasks.py)   │    │                     │ │
│  └─────────────┘    └─────────────┘    └──────────┬──────────┘ │
│                                                    │            │
│  Parameter:                                        ▼            │
│  - Variablenanzahl        ┌───────────────────────────────────┐│
│  - Prämissenanzahl        │ Validierung:                      ││
│  - Formeltiefe            │ - Hat Lösung?                     ││
│  - Erlaubte Operatoren    │ - Nicht-trivial?                  ││
│  - Operator-Gewichte      │ - Level-adäquat?                  ││
│                           └───────────────────────────────────┘│
│                                        │                        │
│                                        ▼                        │
│                           ┌───────────────────────────────────┐│
│                           │ Task-Objekt speichern in DB       ││
│                           │ (apps/generate_tasks/models.py)   ││
│                           └───────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Pre-Generation Strategie

**Problem:** CASE_SPLIT Level 3 kann mehrere Sekunden zur Generierung benötigen.

**Lösung:** Tasks werden vorab generiert und in einem Pool gehalten.

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRE-GENERATION POOL                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Konfiguration: TARGET_TASKS_PER_COMBINATION = 200       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Pool-Status (Beispiel):                                        │
│  ┌────────────────────┬───────────────────┬────────────────┐   │
│  │ Kombination        │ Verfügbar         │ Status         │   │
│  ├────────────────────┼───────────────────┼────────────────┤   │
│  │ DIRECT_INFERENCE/1 │ 198/200           │ ✓              │   │
│  │ DIRECT_INFERENCE/2 │ 200/200           │ ✓              │   │
│  │ CASE_SPLIT/1       │ 45/200            │ Refill nötig   │   │
│  │ CASE_SPLIT/3       │ 200/200           │ ✓              │   │
│  └────────────────────┴───────────────────┴────────────────┘   │
│                                                                 │
│  Nachfüll-Mechanismus:                                          │
│  1. User löst Aufgabe → Attempt wird erstellt                   │
│  2. Django Signal triggert (signals.py)                         │
│  3. Prüfung: Pool < TARGET?                                     │
│  4. Wenn ja: Async-Thread generiert fehlende Tasks              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 CLI-Command `prefill_tasks`

Ermöglicht manuelles Auffüllen des Pools:

```bash
# Alle Kombinationen parallel auffüllen
python manage.py prefill_tasks

# Nur bestimmte Kombination
python manage.py prefill_tasks --type CASE_SPLIT --level 2

# Status anzeigen
python manage.py prefill_tasks --status
```

---

## 8. Lösungsverifikation und Feedback

### 8.1 Lösungsablauf

```
┌─────────────────────────────────────────────────────────────────┐
│                    LÖSUNGSVERIFIKATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. User sendet Antworten                                       │
│     POST /api/solve/ { task_id: 1, answers: {A: "wahr", ...} }  │
│                          │                                      │
│                          ▼                                      │
│  2. Backend lädt Task aus DB                                    │
│                          │                                      │
│                          ▼                                      │
│  3. Cache-Check: Lösung bereits berechnet?                      │
│     ┌────────┬────────┐                                         │
│     │  Ja    │  Nein  │                                         │
│     └───┬────┴───┬────┘                                         │
│         │        │                                              │
│         │        ▼                                              │
│         │   4. Core-Task erstellen                              │
│         │      (DB-Task → SymPy-Formeln)                        │
│         │        │                                              │
│         │        ▼                                              │
│         │   5. BucketElimination.solve()                        │
│         │        │                                              │
│         │        ▼                                              │
│         │   6. Lösung cachen                                    │
│         │        │                                              │
│         └────────┼──────────────────────────────────────────    │
│                  ▼                                              │
│  7. Antworten vergleichen                                       │
│     User-Antwort == Korrekte Lösung?                            │
│                  │                                              │
│                  ▼                                              │
│  8. Fortschritt aktualisieren (UserProgress, Streak)            │
│                  │                                              │
│                  ▼                                              │
│  9. Response mit Ergebnissen                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Feedback-Generierung

```
┌─────────────────────────────────────────────────────────────────┐
│                    FEEDBACK-ENGINE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Eingabe: (Variable, User-Antwort, Korrekte Lösung)             │
│                          │                                      │
│                          ▼                                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ Fallunterscheidung:                                       │ │
│  │                                                           │ │
│  │ A) User == Lösung   → "Korrekt!"                          │ │
│  │                                                           │ │
│  │ B) Lösung = None,   → "Unnötige Annahme"                  │ │
│  │    User ≠ None        + Gegenbeispiel generieren          │ │
│  │                                                           │ │
│  │ C) Lösung ≠ None,   → "Verpasste Schlussfolgerung"        │ │
│  │    User = None        + Hinweis auf zwingende Folgerung   │ │
│  │                                                           │ │
│  │ D) User ≠ Lösung    → "Falsche Belegung"                  │ │
│  │    (beide ≠ None)     + Korrektur                         │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Gegenbeispiel-Generierung (Fall B):                            │
│  - Suche Szenario wo Variable den gegenteiligen Wert hat        │
│  - Alle Prämissen müssen trotzdem erfüllt sein                  │
│  - Zeige konkretes Beispiel als Beweis                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. API-Kommunikation

### 9.1 Authentifizierung

Die Anwendung verwendet **Session-basierte Authentifizierung**:

```
┌────────────┐                            ┌─────────────┐
│  Frontend  │                            │   Backend   │
└─────┬──────┘                            └──────┬──────┘
      │                                          │
      │  POST /api/auth/login/                   │
      │  {username, password}                    │
      │─────────────────────────────────────────►│
      │                                          │
      │  Set-Cookie: sessionid=abc123            │
      │  Set-Cookie: csrftoken=xyz789            │
      │◄─────────────────────────────────────────│
      │                                          │
      │  Folgende Requests:                      │
      │  Cookie: sessionid=abc123                │
      │  X-CSRFToken: xyz789                     │
      │─────────────────────────────────────────►│
      │                                          │
```

### 9.2 CORS-Konfiguration

Im Development-Modus (Vite auf Port 5173, Django auf 8000) ist CORS konfiguriert:

- `CORS_ALLOWED_ORIGINS` in `settings.py`
- `CORS_ALLOW_CREDENTIALS = True` für Session-Cookies
- Vite Proxy leitet `/api` an Django weiter

### 9.3 API-Endpunkte (Übersicht)

| Kategorie | Endpunkt | Methode | Beschreibung |
|-----------|----------|---------|--------------|
| **Auth** | `/api/auth/register/` | POST | Registrierung |
| | `/api/auth/login/` | POST | Anmeldung |
| | `/api/auth/logout/` | POST | Abmeldung |
| | `/api/auth/me/` | GET | Aktueller User |
| **Tasks** | `/api/tasks/generate/` | POST | Task anfordern |
| | `/api/tasks/pool_status/` | GET | Pool-Status |
| **Solving** | `/api/solve/` | POST | Lösung einreichen |
| | `/api/feedback/` | POST | Feedback abrufen |
| | `/api/solution/{id}/` | GET | Lösung abrufen |

---

## 10. Konfigurationsdateien

### 10.1 Root-Verzeichnis

| Datei | Funktion |
|-------|----------|
| `manage.py` | Django CLI Entry Point |
| `requirements.txt` | Python-Dependencies |
| `pyproject.toml` | Python-Projekt-Metadaten (für uv/pip) |
| `.python-version` | Python-Version für uv/pyenv |
| `.gitignore` | Git-Ignore-Regeln |
| `.gitattributes` | Git-Zeilenenden-Konfiguration (LF für .sh, CRLF für .ps1) |
| `LICENSE` | MIT-Lizenz |
| `README.md` | Projekt-Dokumentation |

### 10.2 Frontend-Konfiguration

| Datei | Funktion |
|-------|----------|
| `package.json` | npm-Dependencies und Scripts |
| `vite.config.ts` | Vite Build-Konfiguration, Proxy-Setup |
| `tsconfig.json` | TypeScript-Konfiguration |
| `postcss.config.mjs` | PostCSS für Tailwind |
| `tailwind.config.js` | Tailwind CSS Konfiguration |

### 10.3 Scripts-Verzeichnis

| Script | Funktion |
|--------|----------|
| `setup.ps1` / `setup.sh` | Erstinstallation (venv, Dependencies, Migrations) |
| `start-dev.ps1` / `start-dev.sh` | Startet Dev-Server (Frontend + Backend) |
| `start-production.ps1` / `start-production.sh` | Startet Production-Server |

---

## Zusammenfassung

Der Propositional Logic Trainer kombiniert moderne Web-Technologien mit mathematischer Logik:

1. **Klare Trennung** zwischen UI (React), API (Django) und Logik (Core)
2. **Performance durch Pre-Generation** und Caching
3. **Didaktisches Feedback** durch FeedbackEngine mit Gegenbeispielen
4. **Skalierbarer Pool** mit automatischer Nachgenerierung
5. **Wartbarkeit** durch modulare Architektur und Tests

Die Architektur ermöglicht einfache Erweiterungen (neue Aufgabentypen, zusätzliche Solver, Mobile-App) ohne grundlegende Änderungen.
