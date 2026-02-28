from fastapi.testclient import TestClient
from backend.insights_function.server import app

client = TestClient(app)

def test_get_kpis_defaults():
    res = client.get("/api/kpis")
    assert res.status_code == 200
    data = res.json()
    # basic keys
    assert "revenue_per_week" in data
    assert "units_sold_per_slot" in data
    assert "revenue_by_hour" in data
    assert isinstance(data["revenue_by_hour"], list)


def test_get_kpis_parameters():
    res = client.get("/api/kpis?machines=1&hours=10")
    assert res.status_code == 200
    data = res.json()
    # with only 1 machine should still return list
    assert len(data["revenue_by_hour"]) == 10
