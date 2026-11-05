from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest

from billing.domain.entities import Invoice, Plan, Subscription, Tenant, UsageRecord
from billing.domain.events import SubscriptionActivatedEvent
from billing.domain.value_objects import BillingPeriod, Currency, InvoiceStatus, Money, SubscriptionStatus
from billing.infrastructure.persistence.sql.database import (
    create_db_engine,
    create_session_factory,
    init_db,
)
from billing.infrastructure.persistence.sql.unit_of_work import SqlAlchemyUnitOfWork


@pytest.fixture
def uow():
    engine = create_db_engine("sqlite:///:memory:")
    init_db(engine)
    session_factory = create_session_factory(engine)
    return SqlAlchemyUnitOfWork(session_factory)


def test_tenant_and_plan_sql_persistence(uow):
    tenant = Tenant(id="tenant-sql-1", name="Postgres Enterprise", currency=Currency.RUB)

    with uow:
        uow.tenants.save(tenant)
        uow.commit()

    with uow:
        retrieved_tenant = uow.tenants.get_by_id("tenant-sql-1")
        assert retrieved_tenant is not None
        assert retrieved_tenant.name == "Postgres Enterprise"
        assert retrieved_tenant.currency == Currency.RUB

        plan = Plan(
            id="plan-sql-1",
            tenant_id=tenant.id,
            name="Developer Tier",
            price=Money.from_str("1200.00", Currency.RUB),
            period=BillingPeriod.MONTHLY,
            included_units=200,
            overage_unit_price=Money.from_str("5.00", Currency.RUB),
            trial_days=7,
        )
        uow.plans.save(plan)
        uow.commit()

    with uow:
        retrieved_plan = uow.plans.get_by_id("plan-sql-1")
        assert retrieved_plan is not None
        assert retrieved_plan.name == "Developer Tier"
        assert retrieved_plan.price.amount == Decimal("1200.00")
        assert retrieved_plan.trial_days == 7


def test_subscription_and_invoice_sql_persistence(uow):
    now = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)
    tenant = Tenant(id="tenant-sql-2", name="Fintech Core", currency=Currency.RUB)
    plan = Plan(
        id="plan-sql-2",
        tenant_id=tenant.id,
        name="Business Tier",
        price=Money.from_str("5000.00", Currency.RUB),
        period=BillingPeriod.MONTHLY,
    )
    sub = Subscription(
        id="sub-sql-1",
        tenant_id=tenant.id,
        customer_id="cust-sql-100",
        plan_id=plan.id,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=now,
        current_period_end=now + timedelta(days=30),
    )
    inv = Invoice(
        id="inv-sql-1",
        tenant_id=tenant.id,
        customer_id="cust-sql-100",
        subscription_id=sub.id,
        currency=Currency.RUB,
        idempotency_key="idemp-key-999",
    )
    inv.add_item("Monthly Business Subscription", Money.from_str("5000.00", Currency.RUB))
    inv.issue(due_date=now)

    with uow:
        uow.tenants.save(tenant)
        uow.plans.save(plan)
        uow.subscriptions.save(sub)
        uow.invoices.save(inv)
        uow.commit()

    with uow:
        retrieved_inv = uow.invoices.get_by_idempotency_key("tenant-sql-2", "idemp-key-999")
        assert retrieved_inv is not None
        assert retrieved_inv.total_amount.amount == Decimal("5000.00")
        assert len(retrieved_inv.line_items) == 1

        due_subs = uow.subscriptions.list_due_for_renewal(as_of=now + timedelta(days=35))
        assert len(due_subs) == 1
        assert due_subs[0].id == "sub-sql-1"


def test_unit_of_work_rollback(uow):
    tenant = Tenant(id="tenant-rollback-1", name="To Be Rolled Back", currency=Currency.RUB)

    try:
        with uow:
            uow.tenants.save(tenant)
            # Intentionally simulate exception before commit
            raise RuntimeError("Database connection suddenly dropped")
    except RuntimeError:
        pass

    with uow:
        retrieved = uow.tenants.get_by_id("tenant-rollback-1")
        assert retrieved is None  # Rollback succeeded, no dirty state leaked!


def test_transactional_outbox_persistence(uow):
    event = SubscriptionActivatedEvent(
        tenant_id="tenant-sql-outbox",
        subscription_id="sub-12345",
        period_start=datetime.now(timezone.utc),
        period_end=datetime.now(timezone.utc) + timedelta(days=30),
    )

    with uow:
        uow.outbox.save_event(event)
        uow.commit()

    with uow:
        pending_events = uow.outbox.list_unpublished(limit=10)
        assert len(pending_events) == 1
        assert pending_events[0].tenant_id == "tenant-sql-outbox"

        uow.outbox.mark_published(pending_events[0].event_id)
        uow.commit()

    with uow:
        remaining_events = uow.outbox.list_unpublished(limit=10)
        assert len(remaining_events) == 0
