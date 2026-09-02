# ImpactVerse — Citizen Problem Management Platform
## Smart India Hackathon 2026 | Team SIH26043

A full-stack civic-tech platform connecting citizens, universities, and government to report, classify, and resolve societal problems across Jharkhand.

---

## Repository Structure

```
impactverse/
├── main.py              ← AI/ML microservice (Shanur)
├── requirements.txt     ← Python deps
├── test_classify.py     ← AI service tests
│
└── frontend/            ← React frontend (this guide)
    ├── src/
    │   ├── App.jsx                         ← Router root
    │   ├── i18n.js                         ← 🌐 English + Hindi translations
    │   ├── api.js                          ← API layer (mock/live toggle)
    │   ├── components/
    │   │   ├── Nav.jsx                     ← Bilingual nav + language switcher
    │   │   └── ui/                         ← Shared design system
    │   │       ├── Button.jsx
    │   │       ├── Card.jsx
    │   │       ├── Badge.jsx
    │   │       ├── Form.jsx
    │   │       └── index.js
    │   └── pages/
    │       ├── Landing.jsx                 ← Home page
    │       ├── citizen/
    │       │   ├── SubmissionForm.jsx      ← Report a problem (Leaflet + Nominatim)
    │       │   └── PublicTracker.jsx       ← Live tracker (map + filters)
    │       ├── university/
    │       │   └── UniversityDashboard.jsx ← Assigned problems + team form
    │       └── admin/
    │           └── AdminDashboard.jsx      ← Charts + stats + industry interest
    └── tailwind.config.js                  ← Shared design tokens
```

---

## Frontend Quick Start

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

**Prerequisites:** Node.js ≥ 18

---

## Routes

| Path | Screen |
|------|--------|
| `/` | Landing page |
| `/citizen` | Submission form (Leaflet map, Nominatim geocode) |
| `/citizen/tracker` | Public problem tracker (map + list + filters) |
| `/university` | University dashboard (assigned problems, team form) |
| `/admin` | Admin dashboard (Recharts charts, stat cards) |

---

## Switch from Mock → Live API

Open [`frontend/src/api.js`](frontend/src/api.js) and change **one line**:

```js
const USE_MOCK = false   // was: true
```

Set your backend URL in `frontend/.env`:

```
VITE_API_URL=http://localhost:8000
```

---

## Multilingual Support (English + Hindi)

All UI text lives in [`frontend/src/i18n.js`](frontend/src/i18n.js).
The language switcher is in the top utility bar (`EN` / `हिं`).
Preference is persisted to `localStorage`.

---

## AI Microservice (Shanur's piece)

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

See `README.md` → *Problem Classification Service* section for full details.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend framework | React 18 + Vite 5 |
| Styling | Tailwind CSS 3 |
| Maps | Leaflet.js + OpenStreetMap (no API key) |
| Geocoding | Nominatim (free, no API key) |
| Charts | Recharts |
| Routing | React Router v6 |
| AI/ML | FastAPI + sentence-transformers |
| Backend | Santosh's Express/FastAPI service |
