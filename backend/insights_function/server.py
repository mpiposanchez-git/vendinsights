from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import List
from jose import jwt, JWTError
from passlib.context import CryptContext
import os

# use fully qualified package import so uvicorn launched from the
# repository root can locate the modules correctly.
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
except ModuleNotFoundError:
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

import random
import datetime
from typing import Iterator, Any

app = FastAPI()


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


SLOTS = ["A", "B", "C", "D"]


def generate_docs(num_machines: int, hours: int) -> Iterator[dict]:
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
                "timestamp": timestamp.isoformat() + "Z",
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


def verify_password(plain_password: str) -> bool:
    if ADMIN_PASSWORD.startswith("$2"):
        return pwd_context.verify(plain_password, ADMIN_PASSWORD)
    return plain_password == ADMIN_PASSWORD


def create_access_token(username: str) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    expires_at = now + datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": username,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def require_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> str:
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
    docs = list(generate_docs(machines, hours))
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
