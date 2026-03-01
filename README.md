# Vending Insights

A comprehensive telemetry collection, processing, and analysis platform for vending machines. This tool helps vending machine operators monitor real-time performance metrics, track inventory levels, analyze sales trends, and optimize machine operations through data-driven insights.

## Overview

**Vending Insights** is a full-stack application that:

- **Collects telemetry** from vending machines (sales, inventory, temperature, payment status, etc.)
- **Processes data** through a series of microservices to aggregate and enrich telemetry
- **Computes KPIs** (Key Performance Indicators) including revenue, stock-out events, transaction values, temperature stability, and payment error rates
- **Visualizes insights** through an interactive React dashboard showing metrics, trends, and anomalies
- **Simulates telemetry** for testing and demo purposes without physical machines

The platform is designed to scale from prototype to production, with containerized backend functions deployable to Azure, a responsive React frontend for analytics, and comprehensive CI/CD pipelines.

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
4. Starts the frontend dev server on `http://localhost:3000` (if Node/npm are available)
5. Opens the frontend in your default browser or, if the frontend is missing, opens
   the backend `/api/kpis` endpoint directly

The script now automatically runs `npm install` in the `frontend/` directory when
`node_modules` are absent and will fall back to the API URL if the frontend
fails to start or npm isn't installed.

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

- **Frontend Dashboard**: `http://localhost:3000` - View KPIs, charts, and insights
- **Backend API**: `http://localhost:8000/api/kpis` - JSON endpoint with raw metrics

## Architecture & Structure

- `backend/` - Python Azure Functions packaged as containers
  - `insights_function/` - FastAPI server computing and serving KPIs
  - `aggregate_function/` - Data aggregation service
  - `ingest_function/` - Telemetry ingestion handler
  - `ask_function/` - AI-powered query service
  - `email_function/` - Alert and reporting service
  - `tests/` - Unit tests for KPI calculations and API
- `frontend/` - React single-page app for visualizing KPIs and metrics
- `simulator/` - Python script that generates realistic vending machine telemetry
- `.github/workflows/ci.yml` - GitHub Actions CI/CD pipeline
- `azure-pipelines.yml` - Azure DevOps deployment pipeline template
- `decision_log.json` - Architecture and design decisions

## How It Works

### Data Flow

1. **Telemetry Generation**: Vending machines send JSON telemetry (sales, inventory, temperature, etc.)
2. **Ingestion**: Messages arrive via Azure messaging or simulator
3. **Aggregation**: Data is aggregated by machine and time period
4. **Processing**: KPIs are computed in real-time
5. **Visualization**: React frontend fetches metrics and displays interactive charts

## Core KPIs

The following metrics are computed in real-time by the insights service. Helper functions live in `backend/insights_function/kpi_calculations.py` and are covered by unit tests.

### Testing with Simulated Data

A simple telemetry generator is provided under `simulator/vending_simulator.py`. It emits newline-delimited JSON suitable for piping into Azure storage or local tools. Run it with:

```bash
python simulator/vending_simulator.py --machines 5 --hours 168 > sample_data.jsonl
```

This generates 5 days of telemetry data across 5 simulated machines. Adjust `--machines` and `--hours` as needed.

### Backend API

The backend exposes a FastAPI server at `/api/kpis` that returns computed metrics from telemetry. By default it generates three machines worth of hourly data for the past week.

**Running the backend manually:**

```bash
cd backend/insights_function
python -m venv .venv && . .venv/Scripts/activate  # windows
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Then browse `http://localhost:8000/api/kpis` to see the JSON output.

**Running tests:**

The repository includes pytest tests for both KPI calculations and the API. From the `backend` directory:

```bash
python -m pytest
```

### Frontend Dashboard

The React app displays KPI values and interactive charts. It fetches data from `/api/kpis` (or from `public/kpis.json` during development). The dashboard includes:

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

The app will open at `http://localhost:3000`.

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

Deploy containerized functions to Azure using Azure DevOps, Docker, and the provided Bicep/Terraform infrastructure templates. See `azure-pipelines.yml` and `.github/workflows/ci.yml` for CI/CD configuration.

### Free-tier deployment (frontend + protected access)

If you want a zero-cost setup (within free quotas):

1. **Frontend on GitHub Pages**
  - Workflow: `.github/workflows/pages.yml`
  - Add repository secret `REACT_APP_API_BASE_URL` with your backend URL (example: `https://your-backend.onrender.com`).
  - Push to `main` to publish.

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

4. **Login flow**
  - Frontend calls `POST /api/login` with username/password.
  - Backend returns a bearer token.
  - KPI endpoint `GET /api/kpis` requires `Authorization: Bearer <token>`.

> Free-tier note: some free backends sleep after inactivity and have monthly usage limits.

### Docker Build

Each backend function has a Dockerfile:

```bash
docker build -t vendinsights/insights:latest backend/insights_function
docker build -t vendinsights/aggregate:latest backend/aggregate_function
docker build -t vendinsights/ingest:latest backend/ingest_function
```

### Azure Deployment

Use Azure DevOps or GitHub Actions to automatically build and deploy. The CI/CD pipeline runs tests, builds containers, and pushes to your Azure Container Registry.

## Contributing

1. Clone the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python -m pytest` from the `backend` directory
5. Commit and push your changes
6. Open a pull request

## License

This project is provided as-is for learning and demonstration purposes.

