from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from billing.presentation.api.dependencies import ServiceContainer, get_container
from billing.presentation.api.main import create_app


@pytest.fixture
def client():
    app = create_app()
    # Provide a fresh isolated container for testing
    container = ServiceContainer()
    app.dependency_overrides[get_container] = lambda: container
    return TestClient(app)


def test_api_health_and_root(client):
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "version" in res_root.json()

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"


def test_full_subscription_lifecycle_api(client):
    # 1. Create Tenant
    res_tenant = client.post(
        "/api/v1/tenants",
        json={"name": "SaaS Cloud Corp", "currency": "RUB"},
    )
    assert res_tenant.status_code == 201
    tenant_data = res_tenant.json()
    tenant_id = tenant_data["id"]
    assert tenant_data["name"] == "SaaS Cloud Corp"

    # 2. Create Standard Plan (1500 RUB / month, 100 units included, 15 RUB overage)
    res_plan_std = client.post(
        "/api/v1/plans",
        json={
            "tenant_id": tenant_id,
            "name": "Standard Plan",
            "price": "1500.00",
            "currency": "RUB",
            "period": "MONTHLY",
            "included_units": 100,
            "overage_unit_price": "15.00",
            "trial_days": 0,
        },
    )
    assert res_plan_std.status_code == 201
    std_plan_id = res_plan_std.json()["id"]

    # 3. Create Enterprise Plan (5000 RUB / month)
    res_plan_ent = client.post(
        "/api/v1/plans",
        json={
            "tenant_id": tenant_id,
            "name": "Enterprise Plan",
            "price": "5000.00",
            "currency": "RUB",
            "period": "MONTHLY",
            "included_units": 1000,
            "overage_unit_price": "5.00",
            "trial_days": 0,
        },
    )
    assert res_plan_ent.status_code == 201
    ent_plan_id = res_plan_ent.json()["id"]

    # 4. Subscribe customer
    res_sub = client.post(
        "/api/v1/subscriptions",
        json={
            "tenant_id": tenant_id,
            "customer_id": "cust-888",
            "plan_id": std_plan_id,
            "payment_method_id": "card-tok-xyz",
            "idempotency_key": "order-req-001",
        },
    )
    assert res_sub.status_code == 201
    sub_data = res_sub.json()
    subscription_id = sub_data["subscription"]["id"]
    assert sub_data["subscription"]["status"] == "ACTIVE"
    assert sub_data["invoice"]["status"] == "PAID"
    assert Decimal(str(sub_data["invoice"]["total_amount"])) == Decimal("1500.00")

    # 5. Record metered usage
    res_usage = client.post(
        "/api/v1/usage",
        json={
            "tenant_id": tenant_id,
            "subscription_id": subscription_id,
            "metric_name": "compute_hours",
            "units": 80,
        },
    )
    assert res_usage.status_code == 201
    assert res_usage.json()["units"] == 80

    # 6. Change plan to Enterprise (prorated upgrade)
    res_upgrade = client.post(
        f"/api/v1/subscriptions/{subscription_id}/change-plan",
        json={
            "tenant_id": tenant_id,
            "new_plan_id": ent_plan_id,
            "payment_method_id": "card-tok-xyz",
            "idempotency_key": "upgrade-req-001",
        },
    )
    assert res_upgrade.status_code == 200
    upgrade_data = res_upgrade.json()
    assert upgrade_data["subscription"]["plan_id"] == ent_plan_id
    assert "proration" in upgrade_data
    assert Decimal(str(upgrade_data["invoice"]["total_amount"])) > Decimal("0.00")

    # 7. Check Invoices list for this subscription
    res_invs = client.get(f"/api/v1/subscriptions/{subscription_id}/invoices")
    assert res_invs.status_code == 200
    invs_list = res_invs.json()
    assert len(invs_list) == 2  # initial subscription invoice + plan change invoice

    # 8. Run billing cycle
    res_cycle = client.post("/api/v1/billing-cycle/run")
    assert res_cycle.status_code == 200
    assert "renewed_count" in res_cycle.json()
