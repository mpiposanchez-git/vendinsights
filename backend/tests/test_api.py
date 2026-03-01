from fastapi.testclient import TestClient
from backend.insights_function.server import app

client = TestClient(app)


def auth_headers() -> dict:
    login = client.post("/api/login", json={"username": "admin", "password": "changeme"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_login_rejects_bad_credentials():
    res = client.post("/api/login", json={"username": "admin", "password": "wrong"})
    assert res.status_code == 401

def test_get_kpis_defaults():
    res = client.get("/api/kpis", headers=auth_headers())
    assert res.status_code == 200
    data = res.json()
    # basic keys
    assert "revenue_per_week" in data
    assert "units_sold_per_slot" in data
    assert "revenue_by_hour" in data
    assert isinstance(data["revenue_by_hour"], list)


def test_get_kpis_parameters():
    res = client.get("/api/kpis?machines=1&hours=10", headers=auth_headers())
    assert res.status_code == 200
    data = res.json()
    # with only 1 machine should still return list
    assert len(data["revenue_by_hour"]) == 10


def test_get_kpis_requires_auth():
    res = client.get("/api/kpis")
    assert res.status_code == 401
