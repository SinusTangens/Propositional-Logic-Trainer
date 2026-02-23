# npm vs. python manage.py - Zusammenfassung

## Deine Frage beantwortet:

> "Normalerweise sollte man doch nur `python manage.py runserver` ausführen und die Webapp läuft (Frontend + Backend)"

Das stimmt für **klassische Django-Webanwendungen**, aber nicht für **moderne SPA-Architekturen**.

---

## 📊 Vergleich

### Klassisches Django (Alter Stil)

```
┌────────────────────────────────┐
│    Django Server               │
│  ├─ Views (Python)            │
│  ├─ Templates (HTML)          │
│  └─ Static Files (CSS/JS)     │
└────────────────────────────────┘

python manage.py runserver     # Alles läuft hier!
```

**Ablauf:**
1. Browser sendet Request an Django
2. Django rendert HTML mit Python
3. Browser bekommt fertige HTML zurück

---

### Modernes SPA (Unser Setup)

```
┌──────────────┐         ┌──────────────┐
│ React (SPA)  │  JSON   │ Django (API) │
│ Port 3000    │ ◄────►  │ Port 8000    │
└──────────────┘         └──────────────┘

npm run dev               python manage.py runserver
```

**Ablauf:**
1. Browser lädt React-Seite von Port 3000
2. React sendet API-Requests an Port 8000
3. Django antwortet mit JSON, React rendert HTML

---

## ⚡ Was die Befehle bedeuten

### `npm install`
```powershell
npm install
```

**Was:** Installiert alle JavaScript Dependencies aus `package.json`

**Vergleich:** `pip install -r requirements.txt` für Python

**Wann:** Einmalig oder wenn `package.json` ändert sich

**Resultat:** `node_modules/` Verzeichnis wird erstellt (gibt es aber nur auf dem Dev-PC!)

---

### `npm run dev`
```powershell
npm run dev
```

**Was:** Startet **Vite Development Server** auf Port 3000

**Features:**
- 🔥 Hot Module Replacement (HMR) - Änderungen sofort sichtbar!
- 📦 Automatisches Build während Entwicklung
- 🔍 Source Maps für Debugging
- 🚀 VIEL schneller als Production

**Vergleich:** `python manage.py runserver` für Python

**Port:** 3000 (konfigurierbar in `vite.config.ts`)

---

### `npm run build`
```powershell
npm run build
```

**Was:** Erstellt **optimierten Production Build**

**Resultat:** `frontend/dist/` Verzeichnis
```
dist/
├── index.html
├── assets/
│   ├── index-xyz123.js    (minified, hashed)
│   └── style-abc456.css   (minified, hashed)
└── ...
```

**Used in:** Production Mode (`./scripts/start-production.ps1`)

---

### `python manage.py runserver`
```powershell
python manage.py runserver
```

**Was:** Startet **Django Development Server** auf Port 8000

**Features:**
- Automatisches Reload bei Python-Änderungen
- API Endpoints unter `/api/`
- Admin Interface unter `/admin/`
- SQLite Database

**Port:** 8000 (konfigurierbar)

---

## 🎯 Wann nutzt man welche Befehle?

### **Development (Aktive Entwicklung)**

```powershell
# Terminal 1: Backend
.\.venv\Scripts\Activate.ps1
python manage.py runserver

# Terminal 2: Frontend
cd frontend
npm run dev

# ODER: Automatisch
.\scripts\start-dev.ps1
```

**Resultat:**
- Frontend: http://localhost:3000 (Hot Reload aktiv)
- Backend: http://localhost:8000 (Auto-Reload aktiv)
- API: http://localhost:8000/api/

---

### **Production (Produktionsumgebung)**

```powershell
# Automatisch
.\scripts\start-production.ps1

# ODER: Manuell
cd frontend
npm run build
cd ..
.\.venv\Scripts\Activate.ps1
python manage.py collectstatic --noinput
python manage.py runserver
```

**Resultat:**
- Alles: http://localhost:8000
- Django serviert den gebaut React Build
- Frontend ist "statisch" (keine Hot Reload mehr)

---

## 🤔 Sollte man die Befehle in Skripte einbetten?

**Ja! Das haben wir bereits getan:**

```powershell
# Development Mode - Automatisch beide starten
.\scripts\start-dev.ps1

# Production Mode - Bauen + Starten
.\scripts\start-production.ps1
```

**Warum Skripte?**
- ✅ Weniger Tipparbeit
- ✅ Richtige Reihenfolge sichergestellt
- ✅ Fehlerbehandlung
- ✅ Benutzerfreundlich

---

## 📋 Checkliste: Was du wissen solltest

| Befehl | Wann | Resultat |
|--------|------|----------|
| `npm install` | Einmalig | Dependencies installiert |
| `npm run dev` | Development | Frontend läuft auf :3000 mit Hot Reload |
| `npm run build` | Production | Optimiert Build erstellt in `dist/` |
| `python manage.py runserver` | Immer | Backend läuft auf :8000 |
| `python manage.py migrate` | Setup | Datenbank initialisiert |
| `python manage.py createsuperuser` | Setup | Admin-User erstellt |
| `./scripts/start-dev.ps1` | Development | Alles automatisch gestartet |
| `./scripts/start-production.ps1` | Production | Build + Server gestartet |

---

## 🚀 Praktisches Beispiel: Deine erste Änderung

### Szenario: "Ich will die Farbe des Lernpfad-Buttons ändern"

**Step 1: Frontend Development starten**
```powershell
.\scripts\start-dev.ps1
# → Frontend läuft auf :3000, Backend auf :8000
```

**Step 2: Datei ändern**
```typescript
// frontend/src/components/SelectionCard.tsx (Zeile 25)
- className="bg-red-600 hover:bg-red-700"
+ className="bg-blue-600 hover:bg-blue-700"  // Neue Farbe
```

**Step 3: Browser automatisch aktualisiert!**
```
http://localhost:3000
↓
Vite sieht die Änderung
↓
HMR (Hot Module Replacement)
↓
Browser aktualisiert automatisch (OHNE zu reload!)
↓
✅ Neue Farbe sichtbar
```

**Step 4: Speichern für Production**
```powershell
# Wenn fertig mit Entwicklung:
.\scripts\start-production.ps1
# → Frontend wird gebaut (npm run build)
# → Django serviert die neue Version
```

---

## 💡 Pro-Tipps

1. **Niemals manuell `build` während Development** - Macht keinen Sinn, Vite ist da schneller
2. **Immer beide Server laufen** - Frontend braucht Backend für API-Calls
3. **Port-Konflikte?** - Ändern in `.env` oder Config-Dateien
4. **npm vs yarn/pnpm** - npm ist standard, für dieses Projekt ausreichend

---

## ❓ Häufige Fragen

**F: Kann ich nur `npm run dev` machen und das läuft?**
A: Nein, du brauchst auch Backend. Nutze: `.\scripts\start-dev.ps1`

**F: Warum nicht alles in Django?**
A: Modern SPA = bessere UX, schnellere Entwicklung, bessere Skalierbarkeit

**F: Kann man auch `ng serve` nutzen (wie Angular)?**
A: Nein, wir nutzen Vite (schneller) nicht Angular (bereits React)

**F: Was kostet es extra mit npm?**
A: Nichts! Node.js ist kostenlos, npm ist kostenlos

---

## 📚 Weitere Ressourcen

- **Vite:** https://vitejs.dev/guide/why.html
- **npm:** https://docs.npmjs.com/cli/v9/commands/npm
- **Django + Modern Frontend:** https://docs.djangoproject.com/en/stable/howto/deploy/wsgi/
