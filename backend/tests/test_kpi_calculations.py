"""Unit tests for every KPI helper function.

These tests use a tiny deterministic telemetry fixture so expected values are
easy to verify and understand.
"""

import pytest
from backend.insights_function.kpi_calculations import *


@pytest.fixture
def sample_docs():
    """Two telemetry snapshots with intentional value changes."""
    return [
        {"timestamp": "2026-02-28T00:00:00Z",
         "sales": {"revenue_usd": 100, "count": 5},
         "inventory": {"A": 10, "B": 5},
         "temperature_c": 5.0,
         "payment_status": "ok",
         "deviceId": "dev1"},
        {"timestamp": "2026-02-28T01:00:00Z",
         "sales": {"revenue_usd": 50, "count": 2},
         "inventory": {"A": 8, "B": 0},
         "temperature_c": 6.0,
         "payment_status": "error",
         "deviceId": "dev2"},
    ]


def test_revenue_per_week(sample_docs):
    """Revenue should be the sum of all `sales.revenue_usd` values."""
    assert revenue_per_week(sample_docs) == 150


def test_units_sold_per_slot(sample_docs):
    """Sold units are inferred from inventory drop between consecutive snapshots."""
    slots = units_sold_per_slot(sample_docs)
    assert slots["A"] == 2
    assert slots["B"] == 5


def test_stockout_events(sample_docs):
    """Any inventory value at zero counts as one stockout event."""
    assert stockout_events(sample_docs) == 1


def test_avg_transaction_value(sample_docs):
    """Average transaction value equals total revenue divided by total count."""
    assert avg_transaction_value(sample_docs) == pytest.approx(150 / 7)


def test_temperature_stats(sample_docs):
    """Temperature helper should return mean and standard deviation."""
    mean, stdev = temperature_stats(sample_docs)
    assert mean == pytest.approx(5.5)
    assert stdev == pytest.approx(0.70710678)


def test_payment_error_rate(sample_docs):
    """Payment error rate normalizes error events by total transactions."""
    rate = payment_error_rate(sample_docs)
    assert rate == pytest.approx(1 / 7)


def test_active_machines(sample_docs):
    """Distinct device IDs determine active machine count."""
    assert active_machines(sample_docs) == 2


def test_revenue_by_hour(sample_docs):
    """Revenue series should preserve timestamps and corresponding values."""
    result = revenue_by_hour(sample_docs)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["timestamp"] == "2026-02-28T00:00:00Z"
    assert result[0]["revenue"] == 100
    assert result[1]["timestamp"] == "2026-02-28T01:00:00Z"
    assert result[1]["revenue"] == 50
