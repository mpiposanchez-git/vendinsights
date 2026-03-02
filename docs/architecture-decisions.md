# Vending Insights Architecture Decisions

This document is the human-readable ADR companion to [decision_log.json](../decision_log.json).
It captures the core decisions needed to reproduce the current app behavior from scratch.

## 1. Product Scope

- Build a vending-machine monitoring app that computes and displays operational KPIs.
- Keep deployment cost at zero/free tier.
- Ensure local startup is simple for non-expert users.

## 2. System Architecture

## ADR-001: Split frontend and backend

**Decision**
- Use a split architecture: Python API backend + React dashboard frontend.

**Why**
- Clear separation of concerns.
- Independent deployability.
- Easier future scaling of backend services.

**Implementation**
- Backend: `backend/insights_function/server.py`
- Frontend: `frontend/src`

## ADR-002: Keep future microservice placeholders

**Decision**
- Keep `ingest_function`, `aggregate_function`, `ask_function`, and `email_function` as placeholders.

**Why**
- Preserve intended microservice topology without blocking MVP delivery.

## 3. Backend Decisions

## ADR-003: FastAPI as backend framework

**Decision**
- Use FastAPI + Uvicorn + Pydantic.

**Why**
- Fast development cycle.
- Typed models.
- Built-in `/docs` OpenAPI UI.

## ADR-004: Token-based auth with JWT

**Decision**
- Use `POST /api/login` to issue JWT tokens.
- Protect `GET /api/kpis`, `POST /api/ask`, and `GET /api/lumo-mode` using bearer auth dependency.

**Why**
- Stateless and simple for free-tier hosting.

**Env vars**
- `JWT_SECRET`
- `TOKEN_EXPIRE_MINUTES`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`

## ADR-005: Support plaintext and bcrypt passwords

**Decision**
- If `ADMIN_PASSWORD` starts with `$2`, verify as bcrypt hash; otherwise compare plaintext.

**Why**
- Easiest local setup + safer production option.

## ADR-006: Persist telemetry in database (seeded by simulation)

**Decision**
- Store telemetry in a database table and compute KPIs from persisted records.
- Seed data from simulation when the database is empty.

**Why**
- Enables real persistence and cloud DB integration while keeping MVP setup simple.
- Keeps free local mode working via SQLite fallback.

## ADR-007: KPI engine in dedicated module

**Decision**
- Keep KPI calculations in `kpi_calculations.py`.

**Why**
- API stays thin.
- KPI logic becomes testable and reusable.

**KPI set**
- Revenue per week
- Units sold per slot
- Stockout events
- Average transaction value
- Temperature mean/stdev
- Payment error rate
- Active machines
- Revenue by hour

## ADR-020: Local-first Lumo+ strategist

**Decision**
- Implement a local strategy engine for `POST /api/ask` as the default mode (`LUMO_MODE=local`).
- Keep optional OpenAI integration behind mode switch (`LUMO_MODE=auto|openai`).

**Why**
- Works without paid external API.
- Preserves data-grounded insight generation in local/dev environments.
- Allows gradual upgrade to hosted LLM mode when API access is available.

**Behavior**
- Builds recommendations from persisted KPI + telemetry context.
- Produces structured response sections: highlights, risks, business strategies, and machine expansion signal.
- Exposes `GET /api/lumo-mode` so frontend can display active mode badge.

## 4. Frontend Decisions

## ADR-008: React SPA with charting

**Decision**
- Use React + Recharts for dashboard UI.

**Why**
- Fast implementation of basic analytics views.

## ADR-009: Login-gated UI

**Decision**
- Show login form when no token is present.
- Persist token in `localStorage` under `authToken`.

**Why**
- Matches protected backend API.
- Preserves session across refresh.

## ADR-010: Configurable API base URL + fallback mode

**Decision**
- Use `REACT_APP_API_BASE_URL` in API client.
- Optional fallback to `public/kpis.json` when `REACT_APP_ALLOW_SAMPLE_FALLBACK=true`.

**Why**
- Supports separate frontend/backend hosting.
- Allows demo mode if backend is unavailable.

## ADR-011: GitHub Pages path compatibility

**Decision**
- Use `/vendinsights` public path for built frontend.

**Why**
- Repository-based GitHub Pages hosting requires path prefix.

## 5. Local Developer Experience

## ADR-012: One-command local startup

**Decision**
- Use `run_local.py` as primary local launcher.

**Behavior**
- Loads optional root `.env`
- Creates backend virtualenv
- Installs backend dependencies
- Starts backend and frontend
- Opens only one browser tab
- Uses `/docs` for backend readiness and fallback

## ADR-013: Keep secrets local and safe

**Decision**
- Commit `.env.example`; keep real `.env` ignored.

**Why**
- Safe onboarding pattern and no secret leakage in git.

## 6. Testing and Quality

## ADR-014: Backend tests with pytest

**Decision**
- Validate auth behavior and KPI output shape with `backend/tests`.

## ADR-015: Frontend tests with RTL + JSDOM shims

**Decision**
- Test `InsightsPanel` interaction with mocked API.
- Mock `ResizeObserver` in Jest setup for Recharts compatibility.

## ADR-016: Keep test output readable

**Decision**
- Filter known React test-utils deprecation noise in Jest setup.

## 7. Deployment Decisions

## ADR-017: Frontend deploy target = GitHub Pages

**Decision**
- Use `.github/workflows/pages.yml` for build and publish.

## ADR-018: Backend deploy target = free container host

**Decision**
- Deploy backend container to Render (recommended) or Koyeb.

**Required env for hosted backend**
- `JWT_SECRET`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `TOKEN_EXPIRE_MINUTES`
- `ALLOWED_ORIGINS`
- `DATABASE_URL` (optional; if omitted, SQLite is used)

## ADR-019: CORS origin rule

**Decision**
- Set `ALLOWED_ORIGINS` to origin only (no path), e.g. `https://mpiposanchez-git.github.io`.

**Why**
- Prevent CORS mismatch when frontend uses `/vendinsights` path.

## 8. Known Tradeoffs and Next Decisions

- Persistent telemetry is available, but advanced ingestion pipelines are still pending.
- Placeholder services are not implemented yet.
- CI currently allows some steps to continue on lint/test failure (`|| true`), which is useful for iteration but weak for strict release gating.

## 9. Rebuild Blueprint (Condensed)

1. Build FastAPI auth + protected KPI API.
2. Implement KPI math module.
3. Add telemetry persistence layer (SQLite default + optional Postgres via `DATABASE_URL`).
4. Build React login + KPI table + charts.
5. Add API client with env-based base URL.
6. Add local launcher with `.env` support.
7. Add backend/frontend tests.
8. Configure GitHub Pages frontend workflow.
9. Deploy backend container on free host.
10. Set env vars and CORS, then validate end-to-end login + KPI flow.
