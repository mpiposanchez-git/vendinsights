"""FastAPI service that exposes authentication and KPI endpoints.

This file is the runtime heart of the demo backend. It uses synthetic data so
the app works locally without external databases.
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import List
from jose import jwt, JWTError
from passlib.context import CryptContext
import httpx
import os

# Use fully qualified package import so uvicorn launched from the repository
# root can locate modules correctly. Fall back to local imports only when the
# package path itself is unavailable.
try:
    from backend.insights_function.kpi_calculations import (
        revenue_per_week,
        units_sold_per_slot,
        stockout_events,
        avg_transaction_value,
        temperature_stats,
        payment_error_rate,
        active_machines,
        revenue_by_hour,
    )
    from backend.insights_function.database import (
        count_events,
        create_tables,
        fetch_recent_docs,
        insert_telemetry_docs,
        replace_telemetry_docs,
    )
except ModuleNotFoundError as exc:
    if exc.name not in {
        "backend",
        "backend.insights_function.kpi_calculations",
        "backend.insights_function.database",
    }:
        raise

    from kpi_calculations import (
        revenue_per_week,
        units_sold_per_slot,
        stockout_events,
        avg_transaction_value,
        temperature_stats,
        payment_error_rate,
        active_machines,
        revenue_by_hour,
    )
    from database import (
        count_events,
        create_tables,
        fetch_recent_docs,
        insert_telemetry_docs,
        replace_telemetry_docs,
    )

import random
import datetime
from typing import Iterator, Any

app = FastAPI(title="Vending Insights API")


ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
auth_scheme = HTTPBearer()

origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class KPIResponse(BaseModel):
    revenue_per_week: float
    units_sold_per_slot: dict
    stockout_events: int
    avg_transaction_value: float | None
    temperature_mean: float | None
    temperature_stdev: float | None
    payment_error_rate: float | None
    active_machines: int
    revenue_by_hour: List[dict[str, Any]]


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ReseedResponse(BaseModel):
    inserted_rows: int
    total_rows: int
    machines: int
    hours: int


class AskRequest(BaseModel):
    question: str
    machines: int = 3
    hours: int = 168


class AskResponse(BaseModel):
    answer: str


class LumoModeResponse(BaseModel):
    configured_mode: str
    active_mode: str


SLOTS = ["A", "B", "C", "D"]
AUTO_SEED_DATA = os.getenv("AUTO_SEED_DATA", "true").lower() == "true"
SEED_MACHINES = int(os.getenv("SEED_MACHINES", "5"))
SEED_HOURS = int(os.getenv("SEED_HOURS", "336"))
LUMO_MODE = os.getenv("LUMO_MODE", "local").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
LUMO_MODEL = os.getenv("LUMO_MODEL", "gpt-4o-mini")


def generate_docs(num_machines: int, hours: int) -> Iterator[dict]:
    """Generate synthetic telemetry documents.

    Each yielded document mimics one hourly snapshot for one vending machine.
    """
    start = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours)
    for m in range(num_machines):
        device_id = f"machine-{m+1}"
        inventory = {slot: random.randint(5, 20) for slot in SLOTS}
        for h in range(hours):
            timestamp = start + datetime.timedelta(hours=h)
            sold = {slot: random.randint(0, 2) for slot in SLOTS}
            for slot, qty in sold.items():
                inventory[slot] = max(inventory.get(slot, 0) - qty, 0)
            doc = {
                "timestamp": timestamp.astimezone(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
                "deviceId": device_id,
                "inventory": dict(inventory),
                "sales": {
                    "revenue_usd": sum(qty * random.uniform(1.0, 5.0) for qty in sold.values()),
                    "count": sum(sold.values()),
                },
                "temperature_c": round(random.normalvariate(5, 1), 2),
                "payment_status": random.choice(["ok"] * 95 + ["error"] * 5),
            }
            yield doc


def ensure_seeded_data() -> None:
    """Create DB tables and seed synthetic telemetry if storage is empty."""
    create_tables()
    if not AUTO_SEED_DATA:
        return

    if count_events() == 0:
        insert_telemetry_docs(generate_docs(SEED_MACHINES, SEED_HOURS))


def _build_agent_context(docs: list[dict]) -> dict[str, Any]:
    mean_stdev = temperature_stats(docs) or (None, None)
    return {
        "kpis": {
            "revenue_per_week": revenue_per_week(docs),
            "units_sold_per_slot": dict(units_sold_per_slot(docs)),
            "stockout_events": stockout_events(docs),
            "avg_transaction_value": avg_transaction_value(docs),
            "temperature_mean": mean_stdev[0],
            "temperature_stdev": mean_stdev[1],
            "payment_error_rate": payment_error_rate(docs),
            "active_machines": active_machines(docs),
            "revenue_by_hour": revenue_by_hour(docs),
        },
        "sample_telemetry": docs[-20:],
    }


def _ask_openai(question: str, context_payload: dict[str, Any]) -> str:
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Lumo+ is not configured. Set OPENAI_API_KEY in backend environment variables.",
        )

    system_prompt = (
        "You are Lumo+, an operations analyst for vending machine businesses. "
        "Answer only from the provided KPI and telemetry context. "
        "Keep answers practical, concise, and include simple recommendations."
    )

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": LUMO_MODEL,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": (
                            f"Question: {question}\n\n"
                            f"Context JSON:\n{context_payload}"
                        ),
                    },
                ],
            },
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Lumo+ provider error: {response.text}",
        )

    body = response.json()
    return body["choices"][0]["message"]["content"]


def _safe_float(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value)


def _parse_timestamp(ts: str | None) -> datetime.datetime | None:
    if not ts:
        return None
    try:
        return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _machine_rollup(docs: list[dict]) -> dict[str, dict[str, float]]:
    by_machine: dict[str, dict[str, float]] = {}

    for doc in docs:
        machine = str(doc.get("deviceId", "unknown"))
        machine_stats = by_machine.setdefault(
            machine,
            {
                "revenue": 0.0,
                "stockouts": 0.0,
                "payment_errors": 0.0,
                "transactions": 0.0,
            },
        )

        revenue = _safe_float((doc.get("sales") or {}).get("revenue_usd"))
        transactions = _safe_float((doc.get("sales") or {}).get("count"))
        inventory = doc.get("inventory") or {}
        payment_status = str(doc.get("payment_status", ""))

        machine_stats["revenue"] += revenue
        machine_stats["transactions"] += transactions
        machine_stats["stockouts"] += sum(1 for qty in inventory.values() if (qty or 0) == 0)
        if payment_status == "error":
            machine_stats["payment_errors"] += 1

    return by_machine


def _top_machine_insights(docs: list[dict]) -> tuple[str | None, str | None]:
    machine_rollup = _machine_rollup(docs)
    if not machine_rollup:
        return None, None

    top_revenue_machine = max(machine_rollup, key=lambda machine: machine_rollup[machine]["revenue"])
    top_stockout_machine = max(machine_rollup, key=lambda machine: machine_rollup[machine]["stockouts"])

    return top_revenue_machine, top_stockout_machine


def _recent_revenue_change(docs: list[dict]) -> tuple[float | None, str]:
    ordered = sorted(
        (
            (doc_ts, _safe_float((doc.get("sales") or {}).get("revenue_usd")))
            for doc in docs
            for doc_ts in [_parse_timestamp(str(doc.get("timestamp")))]
            if doc_ts is not None
        ),
        key=lambda item: item[0],
    )

    if len(ordered) < 8:
        return None, "insufficient-history"

    revenues = [value for _, value in ordered]
    window = min(24, len(revenues) // 2)
    if window < 4:
        return None, "insufficient-history"

    previous = sum(revenues[-(window * 2): -window])
    recent = sum(revenues[-window:])
    if previous <= 0:
        return None, "flat"

    delta_pct = (recent - previous) / previous
    if delta_pct >= 0.08:
        return delta_pct, "up"
    if delta_pct <= -0.08:
        return delta_pct, "down"
    return delta_pct, "flat"


def _temperature_out_of_range_ratio(docs: list[dict], low: float = 2.0, high: float = 8.0) -> float:
    temps = [doc.get("temperature_c") for doc in docs if doc.get("temperature_c") is not None]
    if not temps:
        return 0.0
    out = sum(1 for temp in temps if float(temp) < low or float(temp) > high)
    return out / len(temps)


def _capacity_signal(machine_rollup: dict[str, dict[str, float]], stockout_ratio: float) -> tuple[bool, str]:
    if not machine_rollup:
        return False, "Not enough machine-level data yet to assess expansion."

    total_revenue = sum(stats["revenue"] for stats in machine_rollup.values())
    if total_revenue <= 0:
        return False, "Revenue is currently too low to justify expansion."

    top_machine = max(machine_rollup, key=lambda machine: machine_rollup[machine]["revenue"])
    top_revenue_share = machine_rollup[top_machine]["revenue"] / total_revenue
    top_stockouts = machine_rollup[top_machine]["stockouts"]

    should_expand = top_revenue_share >= 0.35 and stockout_ratio >= 0.12 and top_stockouts >= 15
    if should_expand:
        return True, (
            f"Expansion signal is strong: {top_machine} contributes {top_revenue_share:.0%} of revenue "
            f"with recurring stockout pressure. Evaluate adding one machine near that location."
        )

    return False, "No immediate expansion signal; optimize stocking and payment reliability first."


def _machine_with_highest(machine_rollup: dict[str, dict[str, float]], metric: str) -> str | None:
    if not machine_rollup:
        return None
    return max(machine_rollup, key=lambda machine: machine_rollup[machine].get(metric, 0.0))


def _detect_intent(question_text: str) -> str:
    if any(word in question_text for word in ["new machine", "expand", "capacity", "location"]):
        return "expansion"
    if any(word in question_text for word in ["stock", "restock", "inventory", "slot", "out of stock"]):
        return "inventory"
    if any(word in question_text for word in ["payment", "card", "transaction error", "failed payment", "checkout"]):
        return "payment"
    if any(word in question_text for word in ["temperature", "cool", "cooling", "fridge", "refrigeration"]):
        return "temperature"
    if any(word in question_text for word in ["revenue", "sales", "profit", "growth", "decline", "drop", "performance"]):
        return "sales"
    return "general"

    top_revenue_machine = None
    top_stockout_machine = None
    if revenue_by_machine:
        top_revenue_machine = max(revenue_by_machine, key=revenue_by_machine.get)
    if stockout_by_machine:
        top_stockout_machine = max(stockout_by_machine, key=stockout_by_machine.get)

    return top_revenue_machine, top_stockout_machine


def _build_local_answer(question: str, context_payload: dict[str, Any], docs: list[dict]) -> str:
    question_text = (question or "").lower()
    intent = _detect_intent(question_text)
    kpis = context_payload["kpis"]

    revenue = _safe_float(kpis.get("revenue_per_week"))
    avg_ticket = kpis.get("avg_transaction_value")
    payment_error = _safe_float(kpis.get("payment_error_rate"))
    stockouts = int(kpis.get("stockout_events") or 0)
    active = int(kpis.get("active_machines") or 0)
    temp_mean = kpis.get("temperature_mean")
    temp_stdev = kpis.get("temperature_stdev")

    machine_rollup = _machine_rollup(docs)
    top_revenue_machine, top_stockout_machine = _top_machine_insights(docs)
    top_payment_error_machine = _machine_with_highest(machine_rollup, "payment_errors")
    revenue_delta, revenue_trend = _recent_revenue_change(docs)
    temp_out_ratio = _temperature_out_of_range_ratio(docs)

    slot_units = kpis.get("units_sold_per_slot") or {}
    best_slot = max(slot_units, key=slot_units.get) if slot_units else None
    low_slot = min(slot_units, key=slot_units.get) if slot_units else None

    total_slot_events = max(1, sum(len((doc.get("inventory") or {}).keys()) for doc in docs))
    stockout_ratio = stockouts / total_slot_events
    expand_needed, expansion_note = _capacity_signal(machine_rollup, stockout_ratio)

    highlights: list[str] = [
        f"Weekly-equivalent revenue is ${revenue:,.2f} across {active} active machines.",
        f"Stockout pressure is {stockout_ratio:.1%} ({stockouts} stockout events across observed slot snapshots).",
        f"Payment error rate is {payment_error:.2%}.",
    ]

    if revenue_delta is not None:
        direction = "up" if revenue_delta >= 0 else "down"
        highlights.append(f"Recent revenue trend is {direction} {abs(revenue_delta):.1%} versus the prior period.")
    if top_revenue_machine:
        highlights.append(f"Top-performing machine by revenue: {top_revenue_machine}.")
    if best_slot:
        highlights.append(f"Best-selling product slot: {best_slot}.")

    risks: list[str] = []
    if stockout_ratio >= 0.10:
        risks.append("Stockout frequency is high enough to materially limit sales conversion.")
    if payment_error >= 0.03:
        risks.append("Payment failures are above target and can suppress completed transactions.")
    if temp_out_ratio >= 0.10:
        risks.append("Temperature excursions are frequent; product quality and spoilage risk are elevated.")
    if revenue_trend == "down":
        risks.append("Recent revenue direction is negative; validate local demand and replenishment cadence.")
    if not risks:
        risks.append("No severe risk threshold breached in the current window; continue monitoring leading indicators.")

    strategies: list[str] = []
    if stockouts > 0:
        strategies.append(
            f"Rebalance inventory and increase par levels first for {top_stockout_machine or 'machines under stockout pressure'} to recover missed sales."
        )
    if best_slot and low_slot and best_slot != low_slot:
        strategies.append(
            f"Tune assortment: allocate more facings to slot {best_slot} and test price/promo changes for slot {low_slot}."
        )
    if payment_error >= 0.02:
        strategies.append("Run payment terminal diagnostics and network checks on high-error machines within 48 hours.")
    strategies.append(expansion_note)

    if not strategies:
        strategies.append("Maintain current plan and review KPI deltas weekly.")

    action_plan: list[str] = []
    if stockout_ratio >= 0.10:
        action_plan.append("P1 (24h): Refill high-risk machines and raise reorder points for fast-moving slots.")
    if payment_error >= 0.03:
        action_plan.append("P1 (24-48h): Audit payment terminals and connectivity on machines with the most failures.")
    if revenue_trend == "down":
        action_plan.append("P2 (this week): Run a location/product mix review on declining machines and test targeted promos.")
    if temp_out_ratio >= 0.10:
        action_plan.append("P2 (this week): Inspect refrigeration health and calibrate sensors where excursions are frequent.")
    if expand_needed:
        action_plan.append("P3 (this month): Build ROI case for one new machine near the top-performing location.")
    if not action_plan:
        action_plan.append("P2 (this week): Keep current operating plan and monitor KPI deltas daily.")

    direct_answer = ""
    if intent == "inventory":
        direct_answer = (
            f"Inventory focus: prioritize {top_stockout_machine or 'the highest-stockout machine'} first and increase par levels for slot {best_slot or 'top-selling items'} "
            f"to reduce current stockout pressure ({stockout_ratio:.1%})."
        )
    elif intent == "payment":
        direct_answer = (
            f"Payment focus: error rate is {payment_error:.2%}; start diagnostics on {top_payment_error_machine or 'high-error machines'} and verify terminal/network reliability."
        )
    elif intent == "temperature":
        direct_answer = (
            f"Temperature focus: mean is {float(temp_mean or 0):.2f}°C with {temp_out_ratio:.1%} out-of-range readings; inspect cooling performance where excursions cluster."
        )
    elif intent == "sales":
        if revenue_delta is not None:
            direct_answer = (
                f"Sales focus: revenue trend is {revenue_trend} ({abs(revenue_delta):.1%} change); optimize assortment and restocking on {top_revenue_machine or 'top machines'} to improve throughput."
            )
        else:
            direct_answer = "Sales focus: not enough history for robust trend detection; monitor daily revenue by machine and slot mix changes this week."
    elif intent == "expansion":
        direct_answer = expansion_note
    else:
        direct_answer = "Overall focus: reduce stockout pressure first, then improve payment reliability to unlock conversion gains."

    summary_lines = [
        "Local Lumo+ analysis from your telemetry data:",
        f"- Revenue/week estimate: ${revenue:,.2f}",
        f"- Active machines: {active}",
        f"- Stockout events: {stockouts}",
        f"- Payment error rate: {payment_error:.2%}",
    ]
    if avg_ticket is not None:
        summary_lines.append(f"- Avg transaction value: ${float(avg_ticket):.2f}")
    if temp_mean is not None and temp_stdev is not None:
        summary_lines.append(f"- Temperature: mean {float(temp_mean):.2f}°C (σ={float(temp_stdev):.2f})")
    if top_revenue_machine:
        summary_lines.append(f"- Highest revenue machine: {top_revenue_machine}")
    if best_slot:
        summary_lines.append(f"- Best-selling slot: {best_slot}")
    summary_lines.append(f"- Machine expansion signal: {'YES' if expand_needed else 'NO'}")

    intent_highlight_filters = {
        "inventory": ["Stockout pressure", "Best-selling product slot", "Top-performing machine"],
        "payment": ["Payment error rate", "Top-performing machine", "Recent revenue trend"],
        "temperature": ["Temperature", "Recent revenue trend", "Top-performing machine"],
        "sales": ["Weekly-equivalent revenue", "Recent revenue trend", "Top-performing machine", "Best-selling product slot"],
        "expansion": ["Weekly-equivalent revenue", "Stockout pressure", "Top-performing machine"],
        "general": [],
    }
    filters = intent_highlight_filters.get(intent, [])
    visible_highlights = (
        [item for item in highlights if any(marker in item for marker in filters)]
        if filters
        else highlights
    )
    if not visible_highlights:
        visible_highlights = highlights

    if intent == "inventory":
        strategies = [strategy for strategy in strategies if "stock" in strategy.lower() or "assortment" in strategy.lower() or "inventory" in strategy.lower()] or strategies
    elif intent == "payment":
        strategies = [strategy for strategy in strategies if "payment" in strategy.lower() or "terminal" in strategy.lower()] or strategies
    elif intent == "temperature":
        strategies = [strategy for strategy in strategies if "temperature" in strategy.lower() or "refrigeration" in strategy.lower()] or strategies
    elif intent == "expansion":
        strategies = [strategy for strategy in strategies if "expansion" in strategy.lower() or "machine" in strategy.lower() or "location" in strategy.lower()] or strategies

    answer_lines = summary_lines + [
        "",
        "Direct answer:",
        direct_answer,
    ] + [
        "",
        "Highlights right now:",
    ] + [f"- {item}" for item in visible_highlights] + [
        "",
        "Risks to watch:",
    ] + [f"- {item}" for item in risks] + [
        "",
        "Business strategies:",
    ] + [f"{index + 1}. {item}" for index, item in enumerate(strategies)] + [
        "",
        "Action plan (next 7 days):",
    ] + [f"{index + 1}. {item}" for index, item in enumerate(action_plan)]

    if "why" in question_text or "drop" in question_text or "decline" in question_text:
        answer_lines += [
            "",
            "Likely causes to validate:",
            "- Stockouts reducing conversion opportunities.",
            "- Payment errors causing checkout failures.",
            "- Product mix mismatch across slots.",
        ]

    if "what should i do" in question_text or "next" in question_text or "suggest" in question_text:
        answer_lines += [
            "",
            "Next best action:",
            strategies[0],
        ]

    if "new machine" in question_text or "expand" in question_text or "capacity" in question_text:
        answer_lines += [
            "",
            "Expansion recommendation:",
            expansion_note,
        ]

    return "\n".join(answer_lines)


def _ask_lumo(question: str, context_payload: dict[str, Any], docs: list[dict]) -> str:
    if LUMO_MODE == "openai":
        return _ask_openai(question, context_payload)

    if LUMO_MODE == "auto" and OPENAI_API_KEY:
        return _ask_openai(question, context_payload)

    return _build_local_answer(question, context_payload, docs)


def _active_lumo_mode() -> str:
    if LUMO_MODE == "openai":
        return "openai"
    if LUMO_MODE == "auto" and OPENAI_API_KEY:
        return "openai"
    return "local"


def verify_password(plain_password: str) -> bool:
    """Validate plaintext password against configured admin credential.

    Supports either:
    - plaintext ADMIN_PASSWORD (local demo convenience)
    - bcrypt-hashed ADMIN_PASSWORD (production-safe approach)
    """
    if ADMIN_PASSWORD.startswith("$2"):
        return pwd_context.verify(plain_password, ADMIN_PASSWORD)
    return plain_password == ADMIN_PASSWORD


def create_access_token(username: str) -> str:
    """Create a signed JWT token for authenticated API access."""
    now = datetime.datetime.now(datetime.timezone.utc)
    expires_at = now + datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def require_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> str:
    """Dependency that blocks requests without a valid bearer token."""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return username
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc


@app.post("/api/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    """Authenticate the dashboard user and issue a short-lived access token."""
    if payload.username != ADMIN_USERNAME or not verify_password(payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = create_access_token(payload.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": TOKEN_EXPIRE_MINUTES * 60,
    }


@app.get("/api/kpis", response_model=KPIResponse)
def get_kpis(machines: int = 3, hours: int = 168, _: str = Depends(require_user)):
    """Return computed KPI payload sourced from persisted telemetry records."""
    ensure_seeded_data()
    docs = fetch_recent_docs(hours=hours, machines=machines)

    if not docs:
        # Fail-safe for brand-new databases where seeding is disabled.
        seed_docs = list(generate_docs(max(1, machines), max(1, hours)))
        insert_telemetry_docs(seed_docs)
        docs = fetch_recent_docs(hours=hours, machines=machines)

    mean_stdev = temperature_stats(docs) or (None, None)
    return {
        "revenue_per_week": revenue_per_week(docs),
        "units_sold_per_slot": units_sold_per_slot(docs),
        "stockout_events": stockout_events(docs),
        "avg_transaction_value": avg_transaction_value(docs),
        "temperature_mean": mean_stdev[0],
        "temperature_stdev": mean_stdev[1],
        "payment_error_rate": payment_error_rate(docs),
        "active_machines": active_machines(docs),
        "revenue_by_hour": revenue_by_hour(docs),
    }


@app.post("/api/reseed", response_model=ReseedResponse)
def reseed_data(machines: int = 5, hours: int = 336, _: str = Depends(require_user)):
    """Replace telemetry dataset with a new simulated batch (no DB growth)."""
    safe_machines = max(1, machines)
    safe_hours = max(1, hours)
    inserted = replace_telemetry_docs(generate_docs(safe_machines, safe_hours))
    total = count_events()
    return {
        "inserted_rows": inserted,
        "total_rows": total,
        "machines": safe_machines,
        "hours": safe_hours,
    }


@app.post("/api/ask", response_model=AskResponse)
def ask_lumo(payload: AskRequest, _: str = Depends(require_user)):
    """Answer user questions from persisted KPI + telemetry context."""
    ensure_seeded_data()
    docs = fetch_recent_docs(hours=max(1, payload.hours), machines=max(1, payload.machines))
    if not docs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No telemetry data available")

    context_payload = _build_agent_context(docs)
    answer = _ask_lumo(payload.question, context_payload, docs)
    return {"answer": answer}


@app.get("/api/lumo-mode", response_model=LumoModeResponse)
def get_lumo_mode(_: str = Depends(require_user)):
    """Return configured and currently active Lumo mode for UI display."""
    return {
        "configured_mode": LUMO_MODE,
        "active_mode": _active_lumo_mode(),
    }
