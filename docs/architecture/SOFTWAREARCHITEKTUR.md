# Softwarearchitektur – Propositional Logic Trainer

Dieses Dokument beschreibt die technische Architektur der Anwendung. Es erklärt die Struktur, Verantwortlichkeiten und Zusammenhänge aller Komponenten.

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
┌──────────────────────────────────────────────────────────────────────────┐
│                          GESAMTARCHITEKTUR                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────┐                    ┌───────────────────────────┐  │
│   │  React Frontend  │  ◄── REST API ──►  │     Django Backend        │  │
│   │  (TypeScript)    │       (JSON)       │     (Python)              │  │
│   │                  │                    │                           │  │
│   │  - UI Components │                    │  ┌─────────────────────┐  │  │
│   │  - State Mgmt    │                    │  │    Django Apps      │  │  │
│   │  - API Service   │                    │  │    (API Layer)      │  │  │
│   └──────────────────┘                    │  └──────────┬──────────┘  │  │
│                                           │       ┌─────┴─────┐       │  │
│                                           │       ▼           ▼       │  │
│                                           │  ┌────────┐ ┌──────────┐  │  │
│                                           │  │ SQLite │ │Core Logic│  │  │
│                                           │  │   DB   │ │ (Solver) │  │  │
│                                           │  └────────┘ └──────────┘  │  │
│                                           └───────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
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

Enthält die Django-Apps, die die REST API bereitstellen.

#### Allgemeine Struktur einer Django-App

Jede App folgt der gleichen Grundstruktur mit standardisierten Dateien:

| Datei | Funktion |
|-------|----------|
| `models.py` | **Datenmodelle** – Definiert Datenbankstrukturen als Python-Klassen (Django ORM). Jede Klasse wird zu einer Tabelle. |
| `views.py` | **Request-Handler** – Empfängt HTTP-Requests, verarbeitet sie und gibt Responses zurück. Enthält die API-Endpunkte. |
| `serializers.py` | **Datenkonvertierung** – Wandelt Python-Objekte in JSON um (und umgekehrt). Validiert eingehende Daten. |
| `urls.py` | **URL-Routing** – Ordnet URL-Pfade den entsprechenden Views zu (z.B. `/api/tasks/` → `TaskViewSet`). |
| `admin.py` | **Admin-Oberfläche** – Registriert Models für das Django Admin Interface (Datenverwaltung im Browser). |
| `apps.py` | **App-Konfiguration** – Metadaten der App (Name, Label). Wird von Django automatisch generiert. |
| `tests.py` | **Unit-Tests** – Automatisierte Tests für die App-Funktionalität. |
| `migrations/` | **Datenbank-Migrationen** – Versionierte Änderungen am Datenbankschema. Automatisch generiert bei Model-Änderungen. |

#### Die vier Apps im Projekt

| App | Zweck | Models | API-Endpunkte |
|-----|-------|--------|---------------|
| **generate_tasks** | Aufgabenverwaltung | `Task` | `/api/tasks/`, `/api/tasks/generate/`, `/api/tasks/pool_status/` |
| **users** | Benutzerverwaltung | `User`, `UserProgress`, `Attempt` | `/api/auth/register/`, `/api/auth/login/`, `/api/auth/logout/`, `/api/auth/me/`, `/api/users/` |
| **solve_tasks** | Lösungsverarbeitung | `SolutionCache` | `/api/solve/`, `/api/feedback/`, `/api/solution/` |
| **feedback** | (Für zukünftiges Feedbacksystem) | – | – |

#### App-spezifische Erweiterungen

**generate_tasks** enthält zusätzliche Dateien:

| Datei | Funktion |
|-------|----------|
| `services.py` | **TaskPreGenerationService** – Singleton für Task-Pool-Management |
| `signals.py` | Django Signal – Triggert automatische Nachgenerierung nach jedem Lösungsversuch |
| `management/commands/` | CLI-Command `prefill_tasks` für manuelles Auffüllen des Pools |

#### Schlüsselkonzepte

**Pre-Generation (generate_tasks):**  
Tasks werden vorab generiert und in der Datenbank gespeichert. Wenn ein Benutzer eine Aufgabe anfordert, wird eine bereits generierte Task aus dem Pool entnommen. Dies vermeidet lange Wartezeiten bei komplexen Aufgabentypen.

**Level-Tracking (users):**  
`UserProgress` speichert den Fortschritt pro Aufgabentyp und Level. Erst nach X aufeinanderfolgenden korrekten Antworten wird das nächste Level freigeschaltet (konfigurierbar in `LEVEL_CONFIG`).

**Caching (solve_tasks):**  
Da das Lösen einer Aufgabe rechenintensiv ist (Bucket Elimination), wird das Ergebnis gecacht. Bei wiederholten Anfragen wird der Cache verwendet.

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
3. Prüfe Aufgabe auf vordefinierte Kriterien
4. Wiederhole bis gültige Aufgabe gefunden
```

### 4.2 `core/logic_engine/solver/`

| Datei | Funktion |
|-------|----------|
| `BooleanTable.py` | Datenstruktur für Wahrheitstabellen (NumPy-basiert) |
| `MarginalSolver.py` | BucketElimination Solver  |

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

**Hinweis zur Erweiterbarkeit:**  
Dies ist die initiale Feedbacklogik. Bei zukünftigem Ausbau (z.B. personalisiertes Feedback, Lernstatistiken, adaptive Hinweise) soll diese Logik in der Django App `apps/feedback/` weitergeführt werden, um eine saubere Trennung zwischen Core-Algorithmen und anwendungsspezifischer Logik zu gewährleisten.

### 4.4 `core/tests/`

| Datei | Funktion |
|-------|----------|
| `bucket_elimination_test.py` | pytest-Tests für den Solver (verifiziert gegen SymPy) |
| `workflow_test.py` | Interaktiver End-to-End Test |

---

## 5. Frontend-Struktur (React)

### 5.1 Verzeichnis `frontend/`

Konfigurationsdateien im Root des Frontend-Verzeichnisses:

| Datei | Funktion |
|-------|----------|
| `index.html` | HTML-Einstiegspunkt – lädt die React-App |
| `package.json` | npm-Konfiguration: Dependencies, Scripts (`dev`, `build`, `preview`) |
| `package-lock.json` | Lock-File für reproduzierbare Builds |
| `vite.config.ts` | Vite-Konfiguration: Dev-Server, Proxy für `/api`, Build-Optionen |
| `tsconfig.json` | TypeScript-Konfiguration für den Quellcode |
| `tsconfig.node.json` | TypeScript-Konfiguration für Vite/Node-Umgebung |
| `postcss.config.mjs` | PostCSS-Konfiguration für Tailwind CSS |
| `.env.example` | Vorlage für Umgebungsvariablen |
| `.gitignore` | Frontend-spezifische Git-Ignore-Regeln |
| `dist/` | Build-Output (generiert durch `npm run build`) |
| `public/` | Statische Assets (werden unverändert kopiert) |

### 5.2 Verzeichnis `frontend/src/`

Quellcode der React-Anwendung:

| Datei | Funktion |
|-------|----------|
| `main.tsx` | **Entry Point** – Rendert die React-App in das DOM |
| `App.tsx` | **Haupt-Komponente** – React Router Setup, Layout-Struktur |

### 5.3 `src/components/`

Wiederverwendbare UI-Komponenten:

| Komponente | Funktion |
|------------|----------|
| `ui/button.tsx` | Button-Komponente mit verschiedenen Varianten |
| `ui/radio-group.tsx` | Radio-Button-Gruppe für Auswahloptionen |
| `AvatarEditor.tsx` | Komponente zur Avatar-Anpassung (Farben, Accessoires) |
| `CelebrationModal.tsx` | Erfolgs-Animation bei Level-Abschluss |
| `SelectionCard.tsx` | Karte für Aufgabentyp-Auswahl auf dem Lernpfad |
| `LogicSymbolsLogo.tsx` | Logo-Komponente mit animierten Logiksymbolen |
| `ScrollToTop.tsx` | Scrollt bei Routenwechsel automatisch nach oben |

### 5.4 `src/pages/`

Seitenkomponenten (entsprechen Routen):

| Seite | Route | Funktion |
|-------|-------|----------|
| `Lernpfad.tsx` | `/lernpfad` | Übersicht der Aufgabentypen und Level (geschützt) |
| `UnitPropagation.tsx` | `/unit-propagation` | Interaktive Aufgabe im Übungungsmodus (DIRECT_INFERENCE) |
| `CaseSplit.tsx` | `/case-split` | Interaktive Aufgabe im Übungsmodus (CASE_SPLIT) |
| `FreiesUeben.tsx` | `/freies-ueben` | Übungsmodus (wird freigeschaltet nach Abschluss des Lernpfades)|
| `Account.tsx` | `/account` | Benutzerprofil, Statistiken, Avatar-Editor |
| `Login.tsx` | `/login` | Anmeldung und Registrierung |
| `Grundlagen.tsx` | `/grundlagen` | Theorie-Seite zur Aussagenlogik |
| `Referenzen.tsx` | `/referenzen` | Vorlesungsunterlagen, Literatur, etc. |
| `Datenschutz.tsx` | `/datenschutz` | Datenschutzerklärung |
| `NotFound.tsx` | `*` | 404-Fehlerseite für unbekannte Routen |

**Hinweis:** Die Startseite (`/`) wird direkt in `App.tsx` als `HomePage`-Komponente definiert und zeigt die Navigations-Karten (Lernpfad, Freies Üben, Grundlagen, Referenzen).

### 5.5 `src/services/`

| Datei | Funktion |
|-------|----------|
| `api.ts` | **Zentraler API-Service** – fetch-Wrapper mit automatischem CSRF-Token-Handling, Basis-URL-Konfiguration, Fehlerbehandlung |

### 5.6 `src/contexts/`

React Context für globalen State:

| Datei | Funktion |
|-------|----------|
| `AuthContext.tsx` | **Authentifizierungsstatus** – Stellt `user`, `login()`, `logout()`, `isAuthenticated` bereit. Speichert User-Daten und Fortschritt. |

### 5.7 `src/lib/`

| Datei | Funktion |
|-------|----------|
| `utils.ts` | Hilfsfunktionen, u.a. `cn()` für bedingte Tailwind-Klassennamen |

### 5.8 `src/styles/`

| Datei | Funktion |
|-------|----------|
| `index.css` | Globale CSS-Styles, Tailwind-Direktiven (`@tailwind base/components/utilities`) |

### 5.9 `src/assets/`

Statische Assets (Bilder):

| Datei | Verwendung |
|-------|------------|
| `hka-logo.jpg` | HKA-Logo für Footer/Header |
| `unit-prop-example.png` | Beispielbild für Unit Propagation Erklärung |
| `case-split-example.png` | Beispielbild für Case Split Erklärung |
| `index.ts` | Export-Datei für einfachen Import der Assets |

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
      │    ┌────────────────┴──────────────┐       │
      │    │                               │       │
      ▼    ▼                               ▼       │
┌─────────────────┐                 ┌──────────────┴───┐
│    Attempt      │                 │  SolutionCache   │
├─────────────────┤                 ├──────────────────┤
│ id              │                 │ id               │
│ user_id (FK)    │                 │ task_id          │
│ task_id (FK)    │                 │ solver_name      │
│ answers         │                 │ result           │
│ is_correct      │                 │ created_at       │
│ created_at      │                 └──────────────────┘
└─────────────────┘
```

### Modell-Beschreibungen

| Modell | App | Beschreibung |
|--------|-----|--------------|
| **User** | `users` | Erweitertes Django-User-Modell (`AbstractUser`). Speichert neben Login-Daten auch Statistiken (`total_solved`, `correct_solved`, `current_streak`, `highscore_streak`) und Avatar-Einstellungen für DiceBear (Hautfarbe, Frisur, Kleidung, etc.). |
| **UserProgress** | `users` | Fortschritt eines Nutzers pro Aufgabentyp. Enthält `current_level`, `correct_in_row` (Streak im aktuellen Level) und `is_completed`. Die Methode `record_answer()` verarbeitet Antworten und triggert Level-Aufstiege. |
| **Attempt** | `users` | Einzelner Lösungsversuch. Verknüpft User und Task, speichert die abgegebene `solution` (JSON), ob sie `is_correct` war, und generiertes `feedback`. |
| **Task** | `generate_tasks` | Vorgenerierte Aufgabe. Enthält `task_type`, `level`, `variables` und Prämissen in zwei Formaten: `premises` (lesbare Unicode-Symbole für Frontend) und `premises_sympy` (SymPy-Repräsentation für Solver). |
| **SolutionCache** | `solve_tasks` | Optionaler Cache für berechnete Solver-Ergebnisse. Speichert `task_id`, `solver_name` und `result` (JSON). Vermeidet wiederholte Berechnungen für dieselbe Aufgabe. |

---

## 7. Aufgabengenerierung und -verwaltung

### 7.1 Generierungspipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUFGABENGENERIERUNG                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐     ┌─────────────────────┐ │
│  │ DIFFICULTY_ │───►│TaskGenerator│───► │ generierte SymPy-   │ │
│  │ CONFIG      │    │             │     │ Formeln (Prämissen) │ │
│  │ (Task.py)   │    │ (generate_  │     │                     │ │
│  │             │    │ tasks.py)   │     │                     │ │
│  └─────────────┘    └─────────────┘     └──────────┬──────────┘ │
│                                                    │            │
│  Parameter:                                        ▼            │
│  - Variablenanzahl         ┌───────────────────────────────────┐│
│  - Prämissenanzahl         │ Validierung:                      ││
│  - Formeltiefe             │ - Hat Lösung?                     ││
│  - Erlaubte Operatoren     │ - Nicht-trivial?                  ││
│  - Operator-Gewichte       │ - Level-adäquat?                  ││
│                            └───────────────────────────────────┘│
│                                        │                        │
│                                        ▼                        │
│                            ┌───────────────────────────────────┐│
│                            │ Task-Objekt speichern in DB       ││
│                            │ (apps/generate_tasks/models.py)   ││
│                            └───────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Pre-Generation Strategie

**Problem:** Komplexere Aufagben haben eine lange Generationszeit.

**Lösung:** Tasks werden vorab generiert und in einem Pool gehalten.

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRE-GENERATION POOL                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Konfiguration: TARGET_TASKS_PER_COMBINATION = 200       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  Pool-Status (Beispiel):                                        │
│  ┌────────────────────┬───────────────────┬────────────────┐    │
│  │ Kombination        │ Verfügbar         │ Status         │    │
│  ├────────────────────┼───────────────────┼────────────────┤    │
│  │ DIRECT_INFERENCE/1 │ 200/200           │ ✓              │    │
│  │ DIRECT_INFERENCE/2 │ 200/200           │ ✓              │    │
│  │ CASE_SPLIT/1       │ 45/200            │ Refill nötig   │    │
│  │ CASE_SPLIT/3       │ 200/200           │ ✓              │    │
│  └────────────────────┴───────────────────┴────────────────┘    │
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
│                      LÖSUNGSVERIFIKATION                        │
│                   "User löst eine Aufgabe"                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Frontend sendet: POST /api/solve/ {task_id: 42, answers: {}}│
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    API LAYER (Views)                    │    │
│  │  - Authentifizierung prüfen                             │    │
│  │  - Request validieren                                   │    │
│  └─────────────────────┬───────────────────────────────────┘    │
│                        │                                        │
│                        ▼                                        │
│  2. ┌──────────────────────────────────────┐                    │
│     │ DATABASE: Task.objects.get(id=42)    │                    │
│     └──────────────────┬───────────────────┘                    │
│                        │                                        │
│                        ▼                                        │
│  3. Cache-Check: Lösung bereits berechnet?                      │
│     ┌────────────────────────────────────────┐                  │
│     │  SolutionCache.objects.filter(task=42) │                  │
│     └───────────┬────────────┬───────────────┘                  │
│                 │            │                                  │
│            [Cache Hit]  [Cache Miss]                            │
│                 │            │                                  │
│                 │            ▼                                  │
│                 │  4. ┌─────────────────────────────────┐       │
│                 │     │      CORE LOGIC (Solver)        │       │
│                 │     │                                 │       │
│                 │     │  - DB-Task → SymPy-Formeln      │       │
│                 │     │  - BucketElimination.solve()    │       │
│                 │     │  - FeedbackEngine.generate()    │       │
│                 │     └──────────────┬──────────────────┘       │
│                 │                    │                          │
│                 │                    ▼                          │
│                 │  5. Lösung in SolutionCache speichern         │
│                 │                    │                          │
│                 └────────┬───────────┘                          │
│                          │                                      │
│                          ▼                                      │
│  6. Antworten vergleichen: User-Lösung == Korrekte Lösung?      │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    API LAYER (Views)                    │    │
│  │  7. Fortschritt aktualisieren (UserProgress, Streak)    │    │
│  │  8. Attempt in DB speichern                             │    │
│  │  9. Response serialisieren                              │    │  
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                      │
│                          ▼                                      │
│  10. Frontend erhält: {is_correct: true, feedback: {...}}       │
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
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Fallunterscheidung:                                       │  │
│  │                                                           │  │
│  │ A) User == Lösung   → "Korrekt!"                          │  │
│  │                                                           │  │
│  │ B) Lösung = None,   → "Unnötige Annahme"                  │  │
│  │    User ≠ None        + Gegenbeispiel generieren          │  │
│  │                                                           │  │
│  │ C) Lösung ≠ None,   → "Verpasste Schlussfolgerung"        │  │
│  │    User = None        + Hinweis auf zwingende Folgerung   │  │
│  │                                                           │  │
│  │ D) User ≠ Lösung    → "Falsche Belegung"                  │  │
│  │    (beide ≠ None)     + Korrektur                         │  │
│  └───────────────────────────────────────────────────────────┘  │
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

### 9.2 CORS- und Cookie-Konfiguration

Im Development-Modus (Vite auf Port 5173, Django auf 8000) ist CORS konfiguriert:

| Einstellung | Wert | Zweck |
|-------------|------|-------|
| `CORS_ALLOWED_ORIGINS` | `localhost:5173`, `127.0.0.1:5173`, ... | Erlaubte Frontend-Origins |
| `CORS_ALLOW_CREDENTIALS` | `True` | Ermöglicht Session-Cookies |
| `CSRF_TRUSTED_ORIGINS` | `localhost:5173`, ... | Vertrauenswürdige Origins für CSRF |
| `SESSION_COOKIE_SAMESITE` | `Lax` | Cookie nur bei Same-Site Requests |
| `CSRF_COOKIE_HTTPONLY` | `False` | JavaScript muss CSRF-Token lesen können |

**Vite Proxy:** Im Development leitet der Vite Dev-Server `/api`-Anfragen an Django (Port 8000) weiter, sodass Frontend und Backend unter derselben Origin erscheinen.

### 9.3 API-Endpunkte (Übersicht)

| Kategorie | Endpunkt | Methode | Beschreibung |
|-----------|----------|---------|--------------|
| **Auth** | `/api/auth/register/` | POST | Neuen Benutzer registrieren |
| | `/api/auth/login/` | POST | Anmeldung (Session erstellen) |
| | `/api/auth/logout/` | POST | Abmeldung (Session beenden) |
| | `/api/auth/me/` | GET | Aktueller User mit Fortschritt |
| | `/api/auth/password-change/` | POST | Passwort ändern |
| | `/api/auth/reset-progress/` | POST | Lernfortschritt zurücksetzen |
| | `/api/auth/avatar/` | PUT | Avatar-Einstellungen speichern |
| | `/api/auth/avatar/random/` | POST | Zufälligen Avatar generieren |
| **Users** | `/api/users/` | GET | Benutzerliste (Admin) |
| | `/api/users/{id}/` | GET | Benutzerdetails (Admin) |
| **Tasks** | `/api/tasks/` | GET | Alle Tasks auflisten |
| | `/api/tasks/{id}/` | GET | Task-Details abrufen |
| | `/api/tasks/generate/` | POST | Neue Task aus Pool anfordern |
| | `/api/tasks/pool_status/` | GET | Pre-Generation Pool Status |
| | `/api/tasks/by_type/` | GET | Tasks nach Typ/Level filtern |
| **Solving** | `/api/solve/` | POST | Lösung einreichen und prüfen |
| | `/api/feedback/` | POST | Detailliertes Feedback abrufen |
| | `/api/solution/{task_id}/` | GET | Komplette Lösung abrufen |

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

Detaillierte Beschreibung siehe [Abschnitt 5.1](#51-verzeichnis-frontend). Die wichtigsten Konfigurationsdateien:

| Datei | Funktion |
|-------|----------|
| `package.json` | npm-Dependencies und Scripts (`dev`, `build`, `preview`) |
| `vite.config.ts` | Vite Build-Konfiguration, Proxy für `/api` → Django |
| `tsconfig.json` | TypeScript-Compiler-Optionen |
| `postcss.config.mjs` | PostCSS-Konfiguration (minimal, da Tailwind 4.x über Vite Plugin läuft) |

**Hinweis:** Tailwind CSS 4.x benötigt keine separate `tailwind.config.js`. Die Konfiguration erfolgt über das Vite Plugin `@tailwindcss/vite` und CSS-Direktiven in `src/styles/index.css`.

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
