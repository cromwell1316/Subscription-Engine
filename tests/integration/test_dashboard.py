import pytest
from fastapi.testclient import TestClient

from billing.presentation.api.dependencies import ServiceContainer, get_container
from billing.presentation.api.main import create_app


@pytest.fixture
def client():
    app = create_app()
    container = ServiceContainer()
    app.dependency_overrides[get_container] = lambda: container
    return TestClient(app)


def test_dashboard_endpoint_html(client):
    res = client.get("/dashboard")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Subscription Engine" in res.text
    assert "Circuit Breaker" in res.text


def test_system_stats_endpoint(client):
    res = client.get("/api/v1/system/stats")
    assert res.status_code == 200
    data = res.json()
    assert "tenants_count" in data
    assert "subscriptions_count" in data
    assert "circuit_breaker" in data
    assert data["circuit_breaker"]["state"] == "CLOSED"


def test_circuit_breaker_manual_controls(client):
    # 1. Trip breaker via API
    res_trip = client.post("/api/v1/system/circuit-breaker/trip")
    assert res_trip.status_code == 200
    assert res_trip.json()["circuit_breaker"]["state"] == "OPEN"

    # Verify stats reflect OPEN
    res_stats = client.get("/api/v1/system/stats")
    assert res_stats.json()["circuit_breaker"]["state"] == "OPEN"

    # 2. Reset breaker via API
    res_reset = client.post("/api/v1/system/circuit-breaker/reset")
    assert res_reset.status_code == 200
    assert res_reset.json()["circuit_breaker"]["state"] == "CLOSED"

    res_stats_after = client.get("/api/v1/system/stats")
    assert res_stats_after.json()["circuit_breaker"]["state"] == "CLOSED"


def test_system_subscriptions_and_invoices_listing(client):
    res_subs = client.get("/api/v1/system/subscriptions")
    assert res_subs.status_code == 200
    subs = res_subs.json()
    assert len(subs) >= 1
    assert subs[0]["customer_id"] == "cust-demo-101"

    res_invs = client.get("/api/v1/system/invoices")
    assert res_invs.status_code == 200
    invs = res_invs.json()
    assert len(invs) >= 1
    assert invs[0]["status"] == "PAID"
