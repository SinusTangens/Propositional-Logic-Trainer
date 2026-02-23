# Propositional Logic Trainer - Frontend

React + TypeScript + Vite Frontend für den Propositional Logic Trainer.

## Entwicklungsumgebung starten

### 1. Dependencies installieren

```powershell
cd frontend
npm install
```

### 2. Development Server starten

```powershell
npm run dev
```

Der Frontend läuft dann auf: **http://localhost:3000**

### 3. Backend parallel starten

In einem separaten Terminal:

```powershell
# Zurück ins Root-Verzeichnis
cd ..

# Virtual Environment aktivieren
.\.venv\Scripts\Activate.ps1

# Django Server starten
python manage.py runserver
```

Das Backend läuft auf: **http://localhost:8000**

## Projekt-Struktur

React + Django (getrennt):
┌─────────────────────┐    API Calls    ┌──────────────────────┐
│  React Frontend     │ ←------------→   │  Django Backend      │
│  (Port 3000)        │     JSON         │  (Port 8000)         │
│  npm run dev        │                  │  manage.py runserver │
└─────────────────────┘                  └──────────────────────┘
      Vite Server                            Python Server


```
frontend/
├── src/
│   ├── components/          # Wiederverwendbare UI-Komponenten
│   │   ├── ui/             # Radix UI Components (Button, etc.)
│   │   ├── SelectionCard.tsx
│   │   └── LogicSymbolsLogo.tsx
│   ├── pages/              # Seiten-Komponenten
│   │   ├── Lernpfad.tsx
│   │   ├── FreiesUeben.tsx
│   │   ├── Grundlagen.tsx
│   │   ├── Referenzen.tsx
│   │   ├── Account.tsx
│   │   ├── UnitPropagation.tsx
│   │   └── CaseSplit.tsx
│   ├── services/           # API Services
│   │   └── api.ts         # Backend-Kommunikation
│   ├── lib/               # Utility Functions
│   │   └── utils.ts
│   ├── styles/            # CSS Styles
│   │   └── index.css
│   ├── App.tsx            # Haupt-App mit Routing
│   └── main.tsx           # Entry Point
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Technologie-Stack

- **React 18.3.1** - UI Framework
- **TypeScript 5.7** - Type Safety
- **Vite 6.3.5** - Build Tool & Dev Server
- **React Router 7.13** - Client-Side Routing
- **Tailwind CSS 4** - Styling
- **Radix UI** - Accessible UI Components
- **Lucide React** - Icons

## API-Integration

Die API-Kommunikation erfolgt über **`src/services/api.ts`**:

```typescript
import { getTasks, submitAttempt } from './services/api';

// Tasks abrufen
const { data: tasks, error } = await getTasks();

// Lösung einreichen
const { data: attempt } = await submitAttempt({
  user_id: 1,
  task_id: 42,
  solution: { A: true, B: false },
  is_correct: true,
  feedback: "Korrekt gelöst!"
});
```

### Verfügbare API-Funktionen

- **Tasks**: `getTasks()`, `getTask(id)`, `createTask(data)`
- **Users**: `getUsers()`, `getUser(id)`, `getCurrentUser()`
- **Attempts**: `getAttempts()`, `getUserAttempts(userId)`, `submitAttempt(data)`
- **Feedback**: `getFeedbackRules()`
- **Cache**: `getSolutionCache(taskId, solverName)`

## Environment Variables

Erstelle eine `.env` Datei im `frontend/` Ordner:

```env
VITE_API_URL=http://localhost:8000/api
```

## Build für Production

```powershell
npm run build
```

Die kompilierten Dateien liegen dann in `frontend/dist/`.

## Nächste Schritte

1. ✅ Frontend-Struktur aufgesetzt
2. ✅ Routing konfiguriert
3. ✅ API-Service vorbereitet
4. ⏳ Backend ViewSets implementieren
5. ⏳ API-Calls in Components integrieren
6. ⏳ Authentifizierung implementieren
7. ⏳ State Management hinzufügen (z.B. Zustand, React Context)

## Troubleshooting

### Module not found Fehler

```powershell
# Node Modules neu installieren
rm -r node_modules
rm package-lock.json
npm install
```

### Port bereits in Verwendung

```powershell
# Ändere Port in vite.config.ts:
server: {
  port: 3001  // Anderer Port
}
```

### CORS-Fehler

Stelle sicher, dass Django CORS korrekt konfiguriert ist:

```python
# backend/logic_trainer/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```
