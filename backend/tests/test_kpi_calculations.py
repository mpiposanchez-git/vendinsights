import pytest
from backend.insights_function.kpi_calculations import *


@pytest.fixture

def sample_docs():
    # simple sequence of two telemetry points for testing (with timestamps)
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
    assert revenue_per_week(sample_docs) == 150


def test_units_sold_per_slot(sample_docs):
    slots = units_sold_per_slot(sample_docs)
    assert slots["A"] == 2
    assert slots["B"] == 5


def test_stockout_events(sample_docs):
    assert stockout_events(sample_docs) == 1


def test_avg_transaction_value(sample_docs):
    assert avg_transaction_value(sample_docs) == pytest.approx(150 / 7)


def test_temperature_stats(sample_docs):
    mean, stdev = temperature_stats(sample_docs)
    assert mean == pytest.approx(5.5)
    assert stdev == pytest.approx(0.70710678)


def test_payment_error_rate(sample_docs):
    rate = payment_error_rate(sample_docs)
    assert rate == pytest.approx(1 / 7)


def test_active_machines(sample_docs):
    assert active_machines(sample_docs) == 2


def test_revenue_by_hour(sample_docs):
    result = revenue_by_hour(sample_docs)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["timestamp"] == "2026-02-28T00:00:00Z"
    assert result[0]["revenue"] == 100
    assert result[1]["timestamp"] == "2026-02-28T01:00:00Z"
    assert result[1]["revenue"] == 50
