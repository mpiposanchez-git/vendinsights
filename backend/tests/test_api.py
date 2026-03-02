"""Integration-style API tests for auth and KPI endpoints."""

import os

from fastapi.testclient import TestClient
from backend.insights_function.server import app

client = TestClient(app)


def auth_headers() -> dict:
    """Log in with default test credentials and return Authorization headers."""
    login = client.post("/api/login", json={"username": "admin", "password": "changeme"})
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_login_rejects_bad_credentials():
    """API should reject incorrect password attempts."""
    res = client.post("/api/login", json={"username": "admin", "password": "wrong"})
    assert res.status_code == 401


def test_get_kpis_defaults():
    """Default KPI request should return the expected response shape."""
    res = client.get("/api/kpis", headers=auth_headers())
    assert res.status_code == 200
    data = res.json()
    # basic keys
    assert "revenue_per_week" in data
    assert "units_sold_per_slot" in data
    assert "revenue_by_hour" in data
    assert isinstance(data["revenue_by_hour"], list)


def test_get_kpis_parameters():
    """Query parameters should control generated machine/hour dimensions."""
    res = client.get("/api/kpis?machines=1&hours=10", headers=auth_headers())
    assert res.status_code == 200
    data = res.json()
    # with only 1 machine should still return list
    assert len(data["revenue_by_hour"]) == 10


def test_get_kpis_requires_auth():
    """KPI endpoint is protected and must return 401 without a token."""
    res = client.get("/api/kpis")
    assert res.status_code == 401


def test_ask_requires_auth():
    """Ask endpoint is protected and must reject unauthenticated requests."""
    res = client.post("/api/ask", json={"question": "hello"})
    assert res.status_code == 403 or res.status_code == 401


def test_ask_returns_local_answer_without_openai_key(monkeypatch):
    """Default local mode should answer even when OPENAI_API_KEY is not configured."""
    monkeypatch.setenv("LUMO_MODE", "local")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    os.environ.pop("OPENAI_API_KEY", None)
    from backend.insights_function import server as server_module

    server_module.LUMO_MODE = "local"
    server_module.OPENAI_API_KEY = None

    res = client.post("/api/ask", headers=auth_headers(), json={"question": "test prompt"})
    assert res.status_code == 200
    answer = res.json()["answer"]
    assert "Highlights right now:" in answer
    assert "Business strategies:" in answer
    assert "Machine expansion signal:" in answer
    assert "Action plan (next 7 days):" in answer


def test_ask_openai_mode_returns_503_without_key(monkeypatch):
    """OpenAI mode should raise a clear configuration error if no API key is set."""
    monkeypatch.setenv("LUMO_MODE", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    os.environ.pop("OPENAI_API_KEY", None)
    from backend.insights_function import server as server_module

    server_module.LUMO_MODE = "openai"
    server_module.OPENAI_API_KEY = None

    res = client.post("/api/ask", headers=auth_headers(), json={"question": "test prompt"})
    assert res.status_code == 503


def test_get_lumo_mode_requires_auth():
    """Lumo mode endpoint must be protected by auth."""
    res = client.get("/api/lumo-mode")
    assert res.status_code == 403 or res.status_code == 401


def test_get_lumo_mode_shape_with_auth():
    """Lumo mode endpoint should return configured and active mode fields."""
    res = client.get("/api/lumo-mode", headers=auth_headers())
    assert res.status_code == 200
    body = res.json()
    assert "configured_mode" in body
    assert "active_mode" in body
