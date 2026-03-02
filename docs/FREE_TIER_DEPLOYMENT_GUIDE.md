# Vending Insights — Free-Tier Deployment Guide

Prefer a one-page version? See [FREE_TIER_DEPLOYMENT_QUICK.md](FREE_TIER_DEPLOYMENT_QUICK.md).

## First-time deployment checklist

- [ ] Deploy backend service on Render (Docker, root directory `backend/insights_function`)
- [ ] Set backend env vars: `JWT_SECRET`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `TOKEN_EXPIRE_MINUTES`
- [ ] (Optional cloud DB) Set `DATABASE_URL` for hosted Postgres
- [ ] Copy backend URL (example: `https://your-service.onrender.com`)
- [ ] Add GitHub secret `REACT_APP_API_BASE_URL` with backend URL
- [ ] Enable GitHub Pages source as **GitHub Actions**
- [ ] Push to `main` (or run Pages workflow manually)
- [ ] Set backend `ALLOWED_ORIGINS` to GitHub Pages origin only (no path)
- [ ] Redeploy backend after env var changes
- [ ] Open frontend URL and sign in
- [ ] Verify KPI table and chart load successfully

This guide deploys your app with:
- **Frontend** on **GitHub Pages** (free)
- **Backend API** on **Render** (free) or **Koyeb** (free)

It is written for this repository’s current setup.

---

## Quick Start (5-minute version)

If you want the shortest path, do this:

1. Deploy backend on **Render** from `backend/insights_function` as a Docker web service.
2. In backend env vars, set:
  - `JWT_SECRET` (strong random string)
  - `ADMIN_USERNAME`
  - `ADMIN_PASSWORD`
  - `TOKEN_EXPIRE_MINUTES=60`
  - `DATABASE_URL` (optional cloud Postgres URL; if omitted, SQLite is used)
3. Copy your backend URL (example: `https://your-service.onrender.com`).
4. In GitHub repo secrets, create `REACT_APP_API_BASE_URL` with that backend URL.
5. Enable GitHub Pages with **GitHub Actions**.
6. Push to `main` to trigger deploy.
7. Set backend `ALLOWED_ORIGINS` to your Pages origin (example: `https://mpiposanchez-git.github.io`).
8. Open your Pages URL and sign in with `ADMIN_USERNAME` + `ADMIN_PASSWORD`.

If anything fails, jump to **Section 7) Quick troubleshooting**.

---

## 1) What you need before starting

- A GitHub account with access to this repo
- A Render account (or Koyeb account)
- Your code pushed to the `main` branch

Optional but recommended:
- A password manager to generate/store secrets

---

## 2) Deploy backend first (Render)

> Do this first because frontend needs the backend URL.

## 2.0 Cloud database (required for persistent hosted data)

If you want hosted persistent telemetry (recommended), set up a free Postgres DB first.

### Option A: Neon (free tier)

1. Create account at Neon and create a new project.
2. Open project dashboard and copy the connection string.
3. Convert it to SQLAlchemy format if needed:
  - from: `postgresql://user:pass@host/db`
  - to: `postgresql+psycopg://user:pass@host/db`
4. Save this as your `DATABASE_URL` value.

#### Neon form setup (recommended values for this app)

When Neon asks for project options:

- **Project name**: `vendinsights` (or any name you prefer)
- **Postgres version**: `17` (good default; supported by SQLAlchemy/psycopg)
- **Cloud service provider**: `AWS` (recommended if backend is on Render)
- **Region**: choose the closest region to your backend host
  - if your Render service is US East, pick **AWS US East 1 (N. Virginia)**
- **Enable Neon Auth**: **No / disabled**

Why disable Neon Auth here:
- This app already has backend auth via `POST /api/login` and JWT.
- Enabling Neon Auth adds a second auth system you are not using now.

### Option B: Supabase (free tier)

1. Create project in Supabase.
2. Go to Database settings and copy the Postgres connection string.
3. Use SQLAlchemy format:
  - `postgresql+psycopg://user:pass@host:5432/postgres`
4. Save this as your `DATABASE_URL` value.

### Which should you pick? (Neon vs Supabase)

Recommended for this project now: **Neon**.

- Pick **Neon** when you only need managed Postgres for this FastAPI backend.
- Pick **Supabase** if you also want extra platform features soon (built-in auth, storage, realtime APIs).

For current app scope (DB-only persistence + free tier): Neon is simpler.

If `DATABASE_URL` is NOT set, backend falls back to local SQLite. That is fine for local development, but not ideal for long-term hosted persistence.

### 2.1 Create the web service

1. Go to Render dashboard → **New +** → **Web Service**.
2. Connect your GitHub repo.
3. Select this repo.
4. Configure:
   - **Environment**: `Docker`
   - **Root Directory**: `backend/insights_function`
   - **Plan**: `Free`
   - **Branch**: `main`
5. Create the service.

### 2.2 Add required environment variables

In Render service settings → **Environment**:

- `JWT_SECRET` = long random string (at least 32 chars)
- `ADMIN_USERNAME` = your login username (example: `admin`)
- `ADMIN_PASSWORD` = your login password (or bcrypt hash)
- `TOKEN_EXPIRE_MINUTES` = `60`
- `ALLOWED_ORIGINS` = your GitHub Pages URL (set in section 3)
- `DATABASE_URL` = optional Postgres URL (Neon/Supabase free tiers)
- `AUTO_SEED_DATA` = optional (`true` by default)
- `SEED_MACHINES` = optional (`5` by default)
- `SEED_HOURS` = optional (`336` by default)

Recommended hosted values:

- `DATABASE_URL=postgresql+psycopg://...`
- `AUTO_SEED_DATA=true`
- `SEED_MACHINES=10`
- `SEED_HOURS=720`

Save changes and redeploy if prompted.

### 2.3 Confirm backend is alive

After deploy, Render gives a URL like:
`https://your-service-name.onrender.com`

Check health from browser:
- `https://your-service-name.onrender.com/docs`

Check login from PowerShell:

```powershell
$body = @{ username = "YOUR_ADMIN_USERNAME"; password = "YOUR_ADMIN_PASSWORD" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "https://your-service-name.onrender.com/api/login" -ContentType "application/json" -Body $body
```

Expected: JSON with `access_token`.

### 2.4 Confirm backend is using cloud database

After first login + KPI request from frontend:

1. Open your Neon/Supabase SQL editor.
2. Run:

```sql
select count(*) as telemetry_rows from telemetry_events;
```

Expected: a number greater than 0.

If this stays 0, your backend may not be using the intended `DATABASE_URL`.

---

## 3) Deploy frontend (GitHub Pages)

This repo already includes a Pages workflow at `.github/workflows/pages.yml`.

### 3.1 Set required GitHub secret

In GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

- Name: `REACT_APP_API_BASE_URL`
- Value: your backend base URL, for example:
  - `https://your-service-name.onrender.com`

### 3.2 Enable GitHub Pages

1. GitHub repo → **Settings** → **Pages**
2. Under **Build and deployment**, choose **GitHub Actions**

### 3.3 Trigger deployment

Push any commit to `main` (or re-run workflow manually).

Workflow used:
- **Deploy to GitHub Pages** (`.github/workflows/pages.yml`)

### 3.4 Get frontend URL

Your site URL format is usually:
- `https://<github-username>.github.io/<repo-name>`

For this repo shape, likely:
- `https://mpiposanchez-git.github.io/vendinsights`

---

## 4) Wire CORS correctly (important)

Now set backend `ALLOWED_ORIGINS` to the exact frontend origin.

Example:
- `ALLOWED_ORIGINS=https://mpiposanchez-git.github.io`

If you include path by mistake (like `/vendinsights`), CORS can fail.
Use **origin only** (scheme + host), no route path.

After editing env vars, redeploy backend.

---

## 5) End-to-end verification checklist

### 5.1 Frontend login

1. Open your GitHub Pages URL
2. Sign in with `ADMIN_USERNAME` and `ADMIN_PASSWORD`
3. Confirm KPI table loads
4. Confirm chart panel loads and metric switch works

### 5.2 API auth manually

PowerShell test:

```powershell
# 1) Login
$loginBody = @{ username = "YOUR_ADMIN_USERNAME"; password = "YOUR_ADMIN_PASSWORD" } | ConvertTo-Json
$login = Invoke-RestMethod -Method Post -Uri "https://your-service-name.onrender.com/api/login" -ContentType "application/json" -Body $loginBody

# 2) Call KPI endpoint with Bearer token
$headers = @{ Authorization = "Bearer $($login.access_token)" }
Invoke-RestMethod -Method Get -Uri "https://your-service-name.onrender.com/api/kpis" -Headers $headers
```

Expected: KPI JSON payload.

### 5.3 DB verification (cloud persistence)

1. Call `/api/kpis` at least once.
2. Re-run SQL query in your cloud DB:

```sql
select count(*) as telemetry_rows from telemetry_events;
```

3. Confirm row count exists and does not reset unexpectedly.

### 5.4 Reseed simulation data (replace-all, no growth)

Use this when you want a fresh simulation dataset without increasing DB size.

PowerShell:

```powershell
$BackendUrl = "https://YOUR-BACKEND-URL"
$Username = "YOUR_ADMIN_USERNAME"
$Password = "YOUR_ADMIN_PASSWORD"

# Login
$loginBody = @{ username = $Username; password = $Password } | ConvertTo-Json
$login = Invoke-RestMethod -Method Post -Uri "$BackendUrl/api/login" -ContentType "application/json" -Body $loginBody

# Reseed (replaces all telemetry rows)
$headers = @{ Authorization = "Bearer $($login.access_token)" }
Invoke-RestMethod -Method Post -Uri "$BackendUrl/api/reseed?machines=10&hours=720" -Headers $headers
```

Notes:

- `machines=10&hours=720` means 10 machines x 720 hourly points (~30 days).
- This endpoint replaces existing telemetry rows, so DB size remains bounded.
- Run this endpoint after deploy whenever you want a new simulation dataset.

---

## 6) Free-tier behavior you should expect

- Free services may **sleep when idle**.
- First request after idle can be slow (cold start).
- Monthly limits apply depending on provider plan.

This is normal for free hosting.

---

## 7) Quick troubleshooting

### Symptom: Login page works but KPI calls fail

Check:
- `REACT_APP_API_BASE_URL` is correct and uses `https`
- Backend is running (open `/docs`)
- `ALLOWED_ORIGINS` matches frontend origin exactly

### Symptom: CORS error in browser console

Fix:
- Set `ALLOWED_ORIGINS` to frontend origin only (no path)
- Redeploy backend

### Symptom: 401 Unauthorized

Check:
- Correct `ADMIN_USERNAME` / `ADMIN_PASSWORD`
- Backend env vars were saved and service redeployed

### Symptom: GitHub Pages does not update

Check:
- `main` branch push happened
- Workflow `.github/workflows/pages.yml` completed successfully
- GitHub Pages source is **GitHub Actions**

---

## 8) Optional backend alternative: Koyeb (free)

If you prefer Koyeb:

1. Create a new **Web Service** from this GitHub repo.
2. Point to `backend/insights_function` Docker context.
3. Add same env vars as section 2.2.
4. Deploy and get public URL.
5. Set GitHub secret `REACT_APP_API_BASE_URL` to Koyeb URL.
6. Keep `ALLOWED_ORIGINS` set to your GitHub Pages origin.

---

## 9) Security minimums for production-like use

- Use a strong `JWT_SECRET`
- Do not keep default `admin/changeme`
- Prefer bcrypt hash for `ADMIN_PASSWORD`
- Restrict `ALLOWED_ORIGINS` to your real frontend origin

---

## 10) One-line deployment order summary

1. Deploy backend (Render/Koyeb) → 2. Set backend env vars → 3. Set `REACT_APP_API_BASE_URL` secret in GitHub → 4. Deploy Pages workflow → 5. Update `ALLOWED_ORIGINS` to frontend origin → 6. Verify login + KPIs.

---

## Appendix A) PowerShell commands only (copy/paste)

Replace placeholders first:
- `YOUR_BACKEND_URL` (example: `https://your-service-name.onrender.com`)
- `YOUR_ADMIN_USERNAME`
- `YOUR_ADMIN_PASSWORD`

### A.1 Login and get token

```powershell
$BackendUrl = "YOUR_BACKEND_URL"
$Username = "YOUR_ADMIN_USERNAME"
$Password = "YOUR_ADMIN_PASSWORD"

$LoginBody = @{ username = $Username; password = $Password } | ConvertTo-Json
$Login = Invoke-RestMethod -Method Post -Uri "$BackendUrl/api/login" -ContentType "application/json" -Body $LoginBody
$Login
```

### A.2 Call protected KPI endpoint

```powershell
$Headers = @{ Authorization = "Bearer $($Login.access_token)" }
Invoke-RestMethod -Method Get -Uri "$BackendUrl/api/kpis" -Headers $Headers
```

### A.3 Verify backend docs page

```powershell
Start-Process "$BackendUrl/docs"
```

### A.4 Quick CORS sanity (manual)

```powershell
Write-Host "Ensure ALLOWED_ORIGINS is exactly your GitHub Pages origin (no path)."
Write-Host "Example: https://mpiposanchez-git.github.io"
```

### A.5 Local quality checks before pushing

```powershell
Set-Location C:\Users\mpipo\Codes\vendinsights
python -m pytest backend/tests -q
npm --prefix frontend test -- --watchAll=false
npm --prefix frontend run build
```

---

## Appendix B) GitHub UI checklist (exact clicks)

Use this when you want a step-by-step click path in GitHub.

### B.1 Add backend URL secret

1. Open your GitHub repository.
2. Click **Settings** (top repo menu).
3. In the left sidebar, click **Secrets and variables** → **Actions**.
4. Click **New repository secret**.
5. Enter:
  - **Name**: `REACT_APP_API_BASE_URL`
  - **Secret**: `https://your-service-name.onrender.com`
6. Click **Add secret**.

### B.2 Enable GitHub Pages deployment source

1. In the same repo, click **Settings**.
2. Left sidebar: **Pages**.
3. Under **Build and deployment**:
  - **Source**: choose **GitHub Actions**.
4. Wait for settings to save.

### B.3 Trigger deployment workflow

Option 1 (recommended):
1. Push a commit to `main`.

Option 2 (manual rerun):
1. Click **Actions** tab.
2. Select workflow **Deploy to GitHub Pages**.
3. Click **Run workflow**.
4. Choose `main` and click **Run workflow**.

### B.4 Confirm deployment completed

1. Go to **Actions** tab.
2. Open latest **Deploy to GitHub Pages** run.
3. Confirm all jobs are green.
4. Open **Settings** → **Pages** and click the published URL.

### B.5 Common GitHub-side mistakes

- Secret name typo (`REACT_APP_API_BASE_URL` must match exactly).
- Pages source not set to **GitHub Actions**.
- Workflow ran on wrong branch (must be `main`).
- Backend URL in secret missing `https://`.

---

## Appendix C) Render UI checklist (exact clicks)

This appendix walks through Render using the current repo structure.

### C.1 Create the backend service

1. Open Render dashboard.
2. Click **New +** → **Web Service**.
3. Connect GitHub (if not already connected).
4. Select repository: `vendinsights`.
5. Configure service:
  - **Name**: choose any (example: `vendinsights-api`)
  - **Branch**: `main`
  - **Region**: closest to your users
  - **Runtime**: `Docker`
  - **Root Directory**: `backend/insights_function`
  - **Plan**: `Free`
6. Click **Create Web Service**.

### C.2 Set environment variables

1. Open your new service.
2. Click **Environment** tab.
3. Add these keys:
  - `JWT_SECRET` = strong random value
  - `ADMIN_USERNAME` = your username
  - `ADMIN_PASSWORD` = your password (or bcrypt hash)
  - `TOKEN_EXPIRE_MINUTES` = `60`
  - `ALLOWED_ORIGINS` = your GitHub Pages origin (no path)
4. Click **Save Changes**.

If prompted, redeploy.

### C.3 Get backend public URL

1. Open **Overview** tab.
2. Copy service URL (example: `https://vendinsights-api.onrender.com`).
3. Paste that into GitHub secret `REACT_APP_API_BASE_URL`.

### C.4 Redeploy after config changes

1. Open **Manual Deploy**.
2. Click **Deploy latest commit**.
3. Wait until status is **Live**.

### C.5 Verify backend quickly

1. Open `https://your-service.onrender.com/docs`.
2. Confirm Swagger page loads.
3. Use Appendix A commands to test `/api/login` and `/api/kpis`.

### C.6 Common Render-side mistakes

- Wrong **Root Directory** (must be `backend/insights_function`).
- Missing env vars (`JWT_SECRET`, credentials).
- `ALLOWED_ORIGINS` includes path (should be origin only).
- Not redeploying after env var changes.
