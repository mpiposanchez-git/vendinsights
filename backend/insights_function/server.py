from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# use fully qualified package import so uvicorn launched from the
# repository root can locate the modules correctly.
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

import random
import datetime
from typing import Iterator, Any

app = FastAPI()


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


SLOTS = ["A", "B", "C", "D"]


def generate_docs(num_machines: int, hours: int) -> Iterator[dict]:
    start = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
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


@app.get("/api/kpis", response_model=KPIResponse)
def get_kpis(machines: int = 3, hours: int = 168):
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
