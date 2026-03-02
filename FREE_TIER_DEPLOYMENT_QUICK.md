# Vending Insights — Ultra-Short Deployment (Free Tier)

Use this when you only want the minimum steps.

## 1) Deploy backend (Render)

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

## 6) If it fails

- 401: username/password mismatch or backend env vars not applied.
- CORS error: wrong `ALLOWED_ORIGINS` (must be origin only).
- Frontend still calling old API: `REACT_APP_API_BASE_URL` secret missing/wrong; rerun Pages workflow.
