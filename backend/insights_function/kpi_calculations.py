"""Core KPI calculation helpers for vending telemetry.

Each function accepts an iterable of telemetry documents (typically a week
of data) and returns the requested metric.  The code mirrors the
pseudo‑code provided in the project plan.
"""

import statistics
from collections import defaultdict
from typing import Iterable, Mapping, Any

Telemetry = Mapping[str, Any]


def revenue_per_week(docs: Iterable[Telemetry]) -> float:
    """Total USD earned from sales in the last 7 days."""
    return sum(doc.get("sales", {}).get("revenue_usd", 0) for doc in docs)


def units_sold_per_slot(docs: Iterable[Telemetry]) -> Mapping[str, int]:
    """Number of items sold per inventory slot.

    This assumes telemetry documents include an "inventory" mapping of
    `slot -> remaining_quantity`.  A caller is responsible for providing
    chronologically ordered docs so that differences can be computed.
    """
    counter: defaultdict[str, int] = defaultdict(int)
    prev_inventory: dict[str, int] | None = None

    for doc in docs:
        inv = doc.get("inventory")
        if inv is None:
            continue
        if prev_inventory is not None:
            for slot, qty in inv.items():
                prev_qty = prev_inventory.get(slot, qty)
                sold = max(prev_qty - qty, 0)
                counter[slot] += sold
        prev_inventory = dict(inv)

    return counter


def stockout_events(docs: Iterable[Telemetry]) -> int:
    """Count of times any slot reached zero inventory in the period."""
    total = 0
    for doc in docs:
        for qty in doc.get("inventory", {}).values():
            if qty == 0:
                total += 1
    return total


def avg_transaction_value(docs: Iterable[Telemetry]) -> float | None:
    """Average revenue per transaction."""
    total_rev = revenue_per_week(docs)
    total_tx = sum(doc.get("sales", {}).get("count", 0) for doc in docs)
    if total_tx == 0:
        return None
    return total_rev / total_tx


def temperature_stats(docs: Iterable[Telemetry]) -> tuple[float, float] | None:
    """Mean & std‑dev of temperature_c. Returns (mean, stdev) or None if unavailable."""
    temps = [doc.get("temperature_c") for doc in docs if "temperature_c" in doc]
    if not temps:
        return None
    return statistics.mean(temps), statistics.stdev(temps) if len(temps) > 1 else 0.0


def payment_error_rate(docs: Iterable[Telemetry]) -> float | None:
    """Percentage of transactions that returned "error"."""
    total_tx = sum(doc.get("sales", {}).get("count", 0) for doc in docs)
    if total_tx == 0:
        return None
    errors = sum(1 for d in docs if d.get("payment_status") == "error")
    return errors / total_tx


def active_machines(docs: Iterable[Telemetry]) -> int:
    """Number of distinct deviceIds that sent telemetry in the period."""
    return len({d.get("deviceId") for d in docs if "deviceId" in d})


def revenue_by_hour(docs: Iterable[Telemetry]) -> list[dict[str, Any]]:
    """Return list of `{timestamp: iso, revenue: float}` sorted by timestamp.

    Assumes each document has an ISO timestamp under "timestamp" and a
    numeric revenue under `sales.revenue_usd`.
    """
    items: list[tuple[str, float]] = []
    for d in docs:
        ts = d.get("timestamp")
        rev = d.get("sales", {}).get("revenue_usd", 0)
        if ts is not None:
            items.append((ts, rev))
    # sort by timestamp string (ISO8601 sorts lexicographically)
    items.sort(key=lambda x: x[0])
    return [{"timestamp": ts, "revenue": rev} for ts, rev in items]
