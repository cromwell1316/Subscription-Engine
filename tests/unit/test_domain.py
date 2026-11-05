from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest

from billing.domain.entities import Invoice, Plan, Subscription, Tenant, UsageRecord
from billing.domain.exceptions import (
    CurrencyMismatchError,
    InvalidMoneyOperationError,
    InvalidStateTransitionError,
    TenantMismatchError,
)
from billing.domain.value_objects import (
    BillingPeriod,
    Currency,
    InvoiceStatus,
    Money,
    SubscriptionStatus,
)


def test_money_operations_and_immutability():
    m1 = Money.from_str("100.50", Currency.RUB)
    m2 = Money.from_str("49.50", Currency.RUB)

    # Addition
    res_add = m1 + m2
    assert res_add.amount == Decimal("150.00")
    assert res_add.currency == Currency.RUB

    # Subtraction
    res_sub = m1 - m2
    assert res_sub.amount == Decimal("51.00")

    # Multiplication
    res_mul = m1 * 2
    assert res_mul.amount == Decimal("201.00")

    # Currency safety
    m_usd = Money.from_str("10.00", Currency.USD)
    with pytest.raises(CurrencyMismatchError):
        _ = m1 + m_usd


def test_subscription_proration_calculation():
    now = datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc)
    period_start = now
    period_end = now + timedelta(days=30)

    standard_plan = Plan(
        id="plan-standard",
        tenant_id="tenant-1",
        name="Standard",
        price=Money.from_str("3000.00", Currency.RUB),
        period=BillingPeriod.MONTHLY,
    )

    premium_plan = Plan(
        id="plan-premium",
        tenant_id="tenant-1",
        name="Premium",
        price=Money.from_str("6000.00", Currency.RUB),
        period=BillingPeriod.MONTHLY,
    )

    sub = Subscription(
        id="sub-1",
        tenant_id="tenant-1",
        customer_id="cust-100",
        plan_id=standard_plan.id,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=period_start,
        current_period_end=period_end,
    )

    # Upgrade exactly halfway through the period (day 15 out of 30)
    change_time = period_start + timedelta(days=15)
    proration = sub.calculate_proration(standard_plan, premium_plan, change_time)

    # Half the month remained:
    # Unspent credit on standard (3000 / 2) = 1500.00 RUB
    # Cost of premium for remaining half (6000 / 2) = 3000.00 RUB
    # Net amount due = 3000 - 1500 = 1500.00 RUB
    assert proration.unspent_credit.amount == Decimal("1500.00")
    assert proration.new_plan_charge.amount == Decimal("3000.00")
    assert proration.net_amount_due.amount == Decimal("1500.00")


def test_invoice_lifecycle_and_invariants():
    inv = Invoice(
        id="inv-001",
        tenant_id="tenant-1",
        customer_id="cust-100",
        subscription_id="sub-1",
        currency=Currency.RUB,
    )

    inv.add_item("Monthly Subscription", Money.from_str("1000.00", Currency.RUB))
    inv.add_item("Overage API units", Money.from_str("250.00", Currency.RUB), quantity=2)

    assert inv.total_amount.amount == Decimal("1500.00")

    # Cannot issue empty invoice or modify issued invoice
    now = datetime.now(timezone.utc)
    inv.issue(due_date=now + timedelta(days=3))
    assert inv.status == InvoiceStatus.PENDING

    with pytest.raises(InvalidStateTransitionError):
        inv.add_item("New item", Money.from_str("100.00", Currency.RUB))

    # Mark paid
    inv.mark_paid(paid_at=now)
    assert inv.status == InvoiceStatus.PAID

    # Cannot void paid invoice
    with pytest.raises(InvalidStateTransitionError):
        inv.void()


def test_tenant_boundary_enforcement():
    plan_tenant_1 = Plan(
        id="p1",
        tenant_id="tenant-1",
        name="Plan 1",
        price=Money.from_str("1000.00", Currency.RUB),
        period=BillingPeriod.MONTHLY,
    )
    plan_tenant_2 = Plan(
        id="p2",
        tenant_id="tenant-2",
        name="Plan 2",
        price=Money.from_str("2000.00", Currency.RUB),
        period=BillingPeriod.MONTHLY,
    )

    sub = Subscription(
        id="sub-1",
        tenant_id="tenant-1",
        customer_id="c-1",
        plan_id=plan_tenant_1.id,
        status=SubscriptionStatus.ACTIVE,
        current_period_start=datetime.now(timezone.utc),
        current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
    )

    with pytest.raises(TenantMismatchError):
        sub.calculate_proration(plan_tenant_1, plan_tenant_2, datetime.now(timezone.utc))
