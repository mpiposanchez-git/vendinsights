# Vending Insights — Ultra-Short Deployment (Free Tier)

Use this when you only want the minimum steps.

## 1) Deploy backend (Render)

### 1.a Create free cloud database first (Neon or Supabase)

1. Create a free Postgres project in Neon or Supabase.
2. Copy connection string and ensure SQLAlchemy format:
   - `postgresql+psycopg://user:password@host:5432/dbname`
3. Keep this value for `DATABASE_URL`.

If using Neon, recommended choices:
- Project: `vendinsights`
- Postgres: `17`
- Provider: `AWS`
- Region: closest to backend (for Render US East, use `AWS US East 1`)
- Neon Auth: **disabled** (app already uses its own JWT login)

1. Render → New + → Web Service → connect this repo.
2. Settings:
   - Runtime: `Docker`
   - Root Directory: `backend/insights_function`
   - Branch: `main`
   - Plan: `Free`
3. Add env vars:
   - `JWT_SECRET` = strong random string
   - `ADMIN_USERNAME` = your username
   - `ADMIN_PASSWORD` = your password
   - `TOKEN_EXPIRE_MINUTES` = `60`
   - `DATABASE_URL` = your free cloud Postgres URL (Neon/Supabase)
   - `AUTO_SEED_DATA` = `true`
   - `SEED_MACHINES` = `10`
   - `SEED_HOURS` = `720`
4. Deploy and copy backend URL (example: `https://your-service.onrender.com`).

## 2) Configure GitHub Pages frontend

1. GitHub repo → Settings → Secrets and variables → Actions.
2. Add secret:
   - `REACT_APP_API_BASE_URL` = backend URL from step 1.
3. GitHub repo → Settings → Pages → Source = **GitHub Actions**.
4. Push to `main` (or Actions → run `Deploy to GitHub Pages`).

## 3) Set CORS correctly

In Render backend env vars, set:
- `ALLOWED_ORIGINS` = GitHub Pages **origin only** (no path)

Example:
- `https://mpiposanchez-git.github.io`

Redeploy backend after saving env vars.

## 4) Verify quickly

- Open backend docs: `https://your-service.onrender.com/docs`
- Open frontend: `https://<github-user>.github.io/<repo-name>`
- Sign in with `ADMIN_USERNAME` + `ADMIN_PASSWORD`
- Confirm KPI table + chart load

Cloud DB check:

```sql
select count(*) as telemetry_rows from telemetry_events;
```

Expected: value greater than 0 after first `/api/kpis` call.

## 5) Copy/paste PowerShell API test

```powershell
$BackendUrl = "https://your-service.onrender.com"
$Username = "YOUR_ADMIN_USERNAME"
$Password = "YOUR_ADMIN_PASSWORD"

$LoginBody = @{ username = $Username; password = $Password } | ConvertTo-Json
$Login = Invoke-RestMethod -Method Post -Uri "$BackendUrl/api/login" -ContentType "application/json" -Body $LoginBody
$Headers = @{ Authorization = "Bearer $($Login.access_token)" }
Invoke-RestMethod -Method Get -Uri "$BackendUrl/api/kpis" -Headers $Headers
```

## 5b) Copy/paste reseed command (replace-all)

```powershell
$BackendUrl = "https://YOUR-BACKEND-URL"
$Username = "YOUR_ADMIN_USERNAME"
$Password = "YOUR_ADMIN_PASSWORD"

$loginBody = @{ username = $Username; password = $Password } | ConvertTo-Json
$login = Invoke-RestMethod -Method Post -Uri "$BackendUrl/api/login" -ContentType "application/json" -Body $loginBody
$headers = @{ Authorization = "Bearer $($login.access_token)" }
Invoke-RestMethod -Method Post -Uri "$BackendUrl/api/reseed?machines=10&hours=720" -Headers $headers
```

This replaces existing telemetry rows with a new simulated batch (no unbounded growth).

## 6) If it fails

- 401: username/password mismatch or backend env vars not applied.
- CORS error: wrong `ALLOWED_ORIGINS` (must be origin only).
- Frontend still calling old API: `REACT_APP_API_BASE_URL` secret missing/wrong; rerun Pages workflow.
- DB row count stays 0: `DATABASE_URL` is missing/wrong in backend env vars.
