# Vending Insights

A comprehensive telemetry collection, processing, and analysis platform for vending machines. This tool helps vending machine operators monitor real-time performance metrics, track inventory levels, analyze sales trends, and optimize machine operations through data-driven insights.

## Overview

**Vending Insights** is a full-stack application that:

- **Collects telemetry** from vending machines (sales, inventory, temperature, payment status, etc.)
- **Processes data** through a series of microservices to aggregate and enrich telemetry
- **Computes KPIs** (Key Performance Indicators) including revenue, stock-out events, transaction values, temperature stability, and payment error rates
- **Visualizes insights** through an interactive React dashboard showing metrics, trends, and anomalies
- **Simulates telemetry** for testing and demo purposes without physical machines

The platform is designed to scale from prototype to production, with a containerized backend, a responsive React frontend for analytics, and CI/CD workflows.

## Docs Index

- `docs/FREE_TIER_DEPLOYMENT_GUIDE.md` - full step-by-step deployment guide (Render + GitHub Pages)
- `docs/FREE_TIER_DEPLOYMENT_QUICK.md` - one-page fast deployment version
- `docs/architecture-decisions.md` - human-readable ADR-style architecture decisions
- `decision_log.json` - machine-readable comprehensive decision log

## Quick Start

### Prerequisites

- Python 3.8+ with pip
- Node.js & npm (for frontend development)
- Git

### Run Locally

From the repository root:

```bash
# Install frontend dependencies (one-time)
cd frontend && npm install && cd ..

# Start the application
python run_local.py
```

`run_local.py` is a convenience launcher that:

1. Creates and activates a Python virtual environment for the backend (if needed)
2. Installs backend dependencies
3. Starts the backend API on `http://localhost:8000`
4. Starts the frontend dev server on `http://localhost:3000/vendinsights` (if Node/npm are available)
5. Opens the frontend in your default browser or, if the frontend is missing, opens
  the backend `/docs` endpoint directly

The script now automatically runs `npm install` in the `frontend/` directory when
`node_modules` are absent and will fall back to the backend docs URL if the frontend
fails to start or npm isn't installed.

For easiest local login setup, copy `.env.example` to `.env` and edit
`ADMIN_USERNAME` / `ADMIN_PASSWORD` once. `run_local.py` automatically loads
values from `.env`.

#### Connectivity diagnostics

If you run into problems contacting the backend (e.g. "connection refused" or a
blank page), there is a helper script:

```bash
python scripts/check_connectivity.py
```

It will attempt HTTP and raw TCP connections against `localhost:8000` and an
external HTTPS URL to help identify VPN/firewall/loopback issues.

Use this script before disabling any VPN or firewall rules.

### Access the Application

- **Frontend Dashboard**: `http://localhost:3000/vendinsights` - Sign in and view KPIs/charts
- **Backend API Docs**: `http://localhost:8000/docs` - Interactive endpoint docs
- **Protected KPI API**: `http://localhost:8000/api/kpis` - Requires bearer token from `/api/login`

## Architecture & Structure

For a detailed rationale behind technical choices, see
`docs/architecture-decisions.md` and `decision_log.json`.

The project is organized as a lightweight full-stack analytics system:

- `backend/` - Python services and tests
  - `insights_function/` - main FastAPI app (`/api/login`, `/api/kpis`) and KPI logic
  - `aggregate_function/` - placeholder entry point for future aggregation microservice
  - `ingest_function/` - placeholder entry point for future ingestion microservice
  - `ask_function/` - placeholder entry point for future natural-language querying
  - `email_function/` - placeholder entry point for future alert/report service
  - `tests/` - pytest suite for KPI calculations and API behavior
- `frontend/` - React dashboard and tests
  - `src/App.jsx` - auth flow, layout, and page composition
  - `src/components/KpiTable.jsx` - tabular KPI rendering
  - `src/components/InsightsPanel.jsx` - chart visualizations (Recharts)
  - `src/components/AskBox.jsx` - placeholder UI section
  - `src/api/client.js` - API client (`login`, `getKpis`) with optional sample fallback
  - `public/kpis.json` - optional sample KPI response for fallback mode
- `simulator/` - telemetry generator script for synthetic device data
- `scripts/` - troubleshooting utilities (connectivity checks)
- `run_local.py` - one-command local launcher for backend + frontend
- `.github/workflows/` - CI and GitHub Pages deployment workflows
- `decision_log.json` - machine-readable architecture and implementation decisions

## Repository Walkthrough

### Backend (`backend/insights_function`)

- `server.py`
  - exposes `POST /api/login` (JWT token issuance)
  - exposes protected `GET /api/kpis` endpoint
  - applies CORS settings from `ALLOWED_ORIGINS`
  - reads telemetry from database and computes KPIs from persisted records
- `kpi_calculations.py`
  - computes revenue, units sold, stockout events, average transaction value
  - computes temperature statistics and payment error rate
  - computes active machine count and time-series revenue by hour
- `database.py`
  - creates DB tables and stores telemetry events
  - supports local SQLite by default and cloud Postgres via `DATABASE_URL`
- `requirements.txt`
  - includes FastAPI, Uvicorn, auth libraries, and test dependencies

### Backend Tests (`backend/tests`)

- `test_api.py`
  - validates login failure handling
  - validates `/api/kpis` response shape
  - validates auth requirement for KPI endpoint
- `test_kpi_calculations.py`
  - unit tests each KPI helper with deterministic fixture data
- `test_sample.py`
  - simple placeholder smoke test

### Frontend (`frontend/src`)

- `App.jsx`
  - renders sign-in form when no token exists
  - stores JWT in `localStorage` and passes token to KPI components
- `api/client.js`
  - centralized fetch wrapper and endpoint helpers
  - optional fallback to `/kpis.json` when `REACT_APP_ALLOW_SAMPLE_FALLBACK=true`
- `components/KpiTable.jsx`
  - fetches and renders KPI values as a table
- `components/InsightsPanel.jsx`
  - fetches KPI payload and visualizes units/revenue as bar charts
- `components/__tests__/InsightsPanel.test.jsx`
  - validates chart render flow and metric switching
- `setupTests.js`
  - Jest setup with `@testing-library/jest-dom` and `ResizeObserver` test mock

### Utility Scripts

- `run_local.py`
  - provisions backend virtual environment
  - installs backend dependencies
  - starts backend (`uvicorn`) and frontend (`npm start`)
  - opens browser and falls back to backend endpoint if frontend cannot start
- `scripts/check_connectivity.py`
  - helps diagnose localhost/network blocks (VPN/firewall/hosts issues)
- `simulator/vending_simulator.py`
  - emits JSONL telemetry for configurable machines and timespan

## How It Works

### Data Flow

1. **Telemetry Generation**: Vending machines send JSON telemetry (sales, inventory, temperature, etc.)
2. **Persistence**: Telemetry is stored in the database (`telemetry_events` table)
3. **Processing**: KPI helpers read persisted telemetry and compute metrics
4. **Visualization**: React frontend fetches protected metrics and displays charts

## Core KPIs

The following metrics are computed in real-time by the insights service. Helper functions live in `backend/insights_function/kpi_calculations.py` and are covered by unit tests.

### Testing with Simulated Data

A simple telemetry generator is provided under `simulator/vending_simulator.py`. It emits newline-delimited JSON suitable for piping into Azure storage or local tools. Run it with:

```bash
python simulator/vending_simulator.py --machines 5 --hours 168 > sample_data.jsonl
```

This generates 5 days of telemetry data across 5 simulated machines. Adjust `--machines` and `--hours` as needed.

### Backend API

The backend exposes a FastAPI server with `POST /api/login` and protected `GET /api/kpis`.
`/api/kpis` reads from database storage. If the database is empty, the app auto-seeds
it with simulated telemetry (configurable via env vars).

Database behavior:

- Default (no `DATABASE_URL`): local SQLite file at `backend/insights_function/vendinsights.db`
- Cloud mode (`DATABASE_URL` set): uses your hosted Postgres database (Neon/Supabase free tiers work)

**Running the backend manually:**

```bash
cd backend/insights_function
python -m venv .venv && . .venv/Scripts/activate  # windows
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Then browse `http://localhost:8000/docs` to authenticate and test the endpoints interactively.

**Running tests:**

The repository includes pytest tests for both KPI calculations and the API. From the `backend` directory:

```bash
python -m pytest
```

### Frontend Dashboard

The React app displays KPI values and interactive charts. After login, it fetches protected data from `/api/kpis` (or from `public/kpis.json` when sample fallback is enabled). The dashboard includes:

- **KPI Table**: Real-time metrics with key statistics
- **Revenue Chart**: Line chart showing revenue trends over time
- **Inventory Chart**: Bar chart showing units sold per machine slot
- **Metric Toggle**: Switch between different KPIs to view trends

**Running the frontend:**

```bash
cd frontend
npm install
npm start
```

The app will open at `http://localhost:3000/vendinsights`.

> **Note**: Node.js & npm required. If you see "npm not found" errors, install Node from [https://nodejs.org/](https://nodejs.org/).

## KPI Definitions

| KPI | Definition | Calculation | Business Value |
|-----|------------|-------------|-----------------|
| **Revenue / week** | Total USD earned from sales in the last 7 days | `sum(doc["sales"]["revenue_usd"] for doc in week_docs)` | Direct measure of business health and profitability |
| **Units sold / slot** | Number of items sold per inventory slot | Count items removed from each slot per time period | Guides stocking decisions and identifies popular products |
| **Stock-out events** | Count of times any slot reached 0 inventory | `sum(1 for d in week_docs for qty in d["inventory"].values() if qty == 0)` | Prevents lost sales from empty machines |
| **Avg transaction value** | Average USD per transaction | `total_revenue / total_transactions` | Indicates upsell opportunities and pricing optimization |
| **Temperature stability** | Mean & std-dev of machine temperature | `mean(temps), stdev(temps)` | Ensures product quality and refrigeration reliability |
| **Payment-error rate** | % of transactions that failed | `errors / total_transactions` | Flags hardware or connectivity issues |
| **Active machines** | Number of machines sending telemetry | `count(distinct deviceId)` | Monitors utilization and identifies downtime |

## Development

### Backend Development

The backend is organized as a Python package with separate functions for different responsibilities:

- **insights_function**: Main API service that computes and serves KPIs
- **aggregate_function**: Aggregates raw telemetry into time-windowed summaries
- **ingest_function**: Entry point for receiving vending machine telemetry
- **ask_function**: AI-powered queries on vending data
- **email_function**: Sends alerts and reports via email

Each function has its own requirements.txt and Dockerfile for containerized deployment.

### Frontend Development

The React frontend provides real-time dashboards with:

- Interactive KPI displays
- Historical trend charts
- Inventory heatmaps
- Payment error tracking
- Machine health monitoring

Built with React, Recharts for visualization, and CSS for responsive design.

## Deployment

Deploy the frontend with GitHub Pages and deploy the backend container to a free host (Render or Koyeb). CI and build checks are defined in `.github/workflows/ci.yml`.

### Free-tier deployment (frontend + protected access)

If you want a zero-cost setup (within free quotas):

1. **Frontend on GitHub Pages (already wired in this repo)**
  - Workflow: `.github/workflows/pages.yml`
  - Add repository secret `REACT_APP_API_BASE_URL` with your backend URL (example: `https://your-backend.onrender.com`).
  - Push to `main` to publish.

  If you specifically need Google-hosted static pages, you can reuse the same `frontend/build` output with Firebase Hosting free tier.

2. **Backend on a free container host**
  - Recommended hosts with free plans: Render or Koyeb.
  - Build from `backend/insights_function/Dockerfile`.
  - Expose port `8000`.

3. **Set backend environment variables**
  - `JWT_SECRET` = strong random secret (required)
  - `ADMIN_USERNAME` = login username for dashboard
  - `ADMIN_PASSWORD` = login password for dashboard
  - `TOKEN_EXPIRE_MINUTES` = token duration (optional, default `60`)
  - `ALLOWED_ORIGINS` = your GitHub Pages origin (optional, comma-separated)
  - `DATABASE_URL` = optional cloud database URL (Postgres). If omitted, SQLite is used.
  - `AUTO_SEED_DATA` = `true`/`false` (optional, default `true`)
  - `SEED_MACHINES` = initial seeded machine count (optional, default `5`)
  - `SEED_HOURS` = seeded hours per machine (optional, default `336`)

4. **Login flow**
  - Frontend calls `POST /api/login` with username/password.
  - Backend returns a bearer token.
  - KPI endpoint `GET /api/kpis` requires `Authorization: Bearer <token>`.

## Quality Checks

The repository currently validates cleanly with:

- Backend tests: `python -m pytest backend/tests -q`
- Frontend tests: `npm --prefix frontend test -- --watchAll=false`
- Frontend production build: `npm --prefix frontend run build`

All three checks pass in the current codebase.

> Free-tier note: some free backends sleep after inactivity and have monthly usage limits.

### Docker Build

Each backend function has a Dockerfile:

```bash
docker build -t vendinsights/insights:latest backend/insights_function
docker build -t vendinsights/aggregate:latest backend/aggregate_function
docker build -t vendinsights/ingest:latest backend/ingest_function
```

## Contributing

1. Clone the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python -m pytest` from the `backend` directory
5. Commit and push your changes
6. Open a pull request

## License

This project is provided as-is for learning and demonstration purposes.

