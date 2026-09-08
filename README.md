# Maoni Yangu — survey platform with location

Standalone survey product in `survey/`: design surveys, collect responses, and optionally capture GPS coordinates on submit.

## Stack

- **Frontend:** Next.js (App Router) + TypeScript + Tailwind — port `7200`
- **Backend:** FastAPI + SQLAlchemy + MySQL (or local SQLite) — port `8200`
- **Maps:** Leaflet + OpenStreetMap tiles on the results page

## Quick start

### Backend

```bash
cd survey/backend
./run.sh
```

API: http://127.0.0.1:8200 · Docs: http://127.0.0.1:8200/docs

### Frontend

```bash
cd survey/frontend
npm install
npm run dev
```

App: http://127.0.0.1:7200

Optional: set `NEXT_PUBLIC_API_URL` if the API is not on `http://127.0.0.1:8200`.

## Free deploy (Render + Vercel)

Repo: [abass254/maoni-yangu](https://github.com/abass254/maoni-yangu)  
Free tiers: API on Render (`*.onrender.com`), frontend on Vercel (`*.vercel.app`).

### 1. Deploy the API on Render

1. Go to [render.com](https://render.com) → **New** → **Web Service** → connect **`abass254/maoni-yangu`**.
2. Settings (important — this repo already has `backend/` at the top level):

| Field | Value |
|--------|--------|
| **Root Directory** | **leave blank** (do **not** use `survey/backend` or `backend`) |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT --app-dir backend` |
| **Instance type** | Free |

3. Environment variables (Render → Environment):

| Key | Value |
|-----|--------|
| `SURVEY_SECRET_KEY` | any long random string (or leave blank and use Render’s generate) |
| `CORS_ORIGINS` | leave empty for now — set after Vercel gives you a URL |
| `PYTHON_VERSION` | `3.12.8` (optional) |

4. Create / **Manual Deploy**. Copy the API URL, e.g. `https://maoni-yangu-api.onrender.com`.
5. Check health: open `https://YOUR-API.onrender.com/api/health` — should return `{"ok":true}` (first load may take ~30–60s on free tier).

### 2. Deploy the frontend on Vercel

1. Go to [vercel.com](https://vercel.com) → **Add New Project** → import **`abass254/maoni-yangu`**.
2. Settings:

| Field | Value |
|--------|--------|
| **Root Directory** | `frontend` |
| **Framework** | Next.js |

3. Environment variable:

| Key | Value |
|-----|--------|
| `NEXT_PUBLIC_API_URL` | your Render URL with **no** trailing slash, e.g. `https://maoni-yangu-api.onrender.com` |

4. Deploy. Copy the site URL, e.g. `https://maoni-yangu.vercel.app`.

### 3. Allow the frontend on the API (CORS)

1. Back on Render → your web service → **Environment**.
2. Set `CORS_ORIGINS` to your Vercel URL, e.g. `https://maoni-yangu.vercel.app` (no trailing slash). Multiple origins: comma-separated.
3. Save — Render redeploys automatically.
4. Open the Vercel URL, register a creator, and create a survey.

### Notes

- Free Render services **sleep** after idle time; the first request after sleep can be slow.
- Set `DATABASE_URL` on Render to your MySQL URL, e.g. `mysql://user:pass@host:3306/survey` (persists across deploys). Without it the API falls back to ephemeral SQLite.
- SQLite (local fallback only) is wiped when the file is deleted; prefer MySQL for production.
- GPS/location needs HTTPS (both Vercel and Render provide it).

## Features

1. Creator auth (register / login)
2. Survey builder — text, multiple choice, rating; draft / publish
3. Public fill-out link at `/s/{public_id}`
4. Required GPS on submit when location collection is enabled
5. Results dashboard — response list, map pins, CSV export

## Location notes

Browsers require HTTPS (or localhost) and user permission for GPS. When a survey collects location, respondents must enable GPS before submit; the API rejects responses without granted coordinates.
