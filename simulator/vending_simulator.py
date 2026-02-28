"""Simple telemetry generator for local testing.

Runs in Azure Cloud Shell or locally, prints newline-delimited JSON documents
representing vending machine telemetry.  Each run emits a week of data, one
document per hour per machine, with randomized values for sales, inventory,
temperature, and status.

Usage: `python vending_simulator.py [--machines N] [--hours H]`
"""

import argparse
import json
import random
import datetime
from typing import Iterator


SLOTS = ["A", "B", "C", "D"]


def generate_docs(num_machines: int, hours: int) -> Iterator[dict]:
    """Yield `hours` telemetry points per machine."""
    start = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
    for m in range(num_machines):
        device_id = f"machine-{m+1}"
        inventory = {slot: random.randint(5, 20) for slot in SLOTS}
        for h in range(hours):
            timestamp = start + datetime.timedelta(hours=h)
            sold = {slot: random.randint(0, 2) for slot in SLOTS}
            # subtract sold from inventory but never drop below zero
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


def run() -> None:
    parser = argparse.ArgumentParser(description="Run vending telemetry simulator")
    parser.add_argument("--machines", type=int, default=3, help="number of devices")
    parser.add_argument("--hours", type=int, default=168, help="hours of data to emit")
    args = parser.parse_args()
    for d in generate_docs(args.machines, args.hours):
        print(json.dumps(d))


if __name__ == '__main__':
    run()
