from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest

from billing.application.ports.clock import FrozenClock
from billing.application.use_cases.change_plan import ChangePlanCommand, ChangePlanUseCase
from billing.application.use_cases.record_usage import RecordUsageCommand, RecordUsageUseCase
from billing.application.use_cases.run_billing_cycle import RunBillingCycleUseCase
from billing.application.use_cases.subscribe_customer import (
    SubscribeCustomerCommand,
    SubscribeCustomerUseCase,
)
from billing.domain.entities import Plan, Tenant
from billing.domain.exceptions import SubscriptionNotActiveError
from billing.domain.value_objects import (
    BillingPeriod,
    Currency,
    InvoiceStatus,
    Money,
    SubscriptionStatus,
)
from billing.infrastructure.gateways.fault_tolerant_gateway import (
    FaultTolerantPaymentGatewayEmulator,
)
from billing.infrastructure.persistence.in_memory_repositories import (
    InMemoryInvoiceRepository,
    InMemoryPlanRepository,
    InMemorySubscriptionRepository,
    InMemoryTenantRepository,
    InMemoryUsageRepository,
)


@pytest.fixture
def test_env():
    start_time = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)
    clock = FrozenClock(start_time)

    tenant_repo = InMemoryTenantRepository()
    plan_repo = InMemoryPlanRepository()
    sub_repo = InMemorySubscriptionRepository()
    inv_repo = InMemoryInvoiceRepository()
    usage_repo = InMemoryUsageRepository()
    gateway = FaultTolerantPaymentGatewayEmulator()

    # Seed base tenant
    tenant = Tenant(id="tenant-alpha", name="Alpha SaaS", currency=Currency.RUB)
    tenant_repo.save(tenant)

    # Seed base plans
    basic_plan = Plan(
        id="plan-basic",
        tenant_id=tenant.id,
        name="Basic Tier",
        price=Money.from_str("1000.00", Currency.RUB),
        period=BillingPeriod.MONTHLY,
        included_units=100,
        overage_unit_price=Money.from_str("10.00", Currency.RUB),
        trial_days=0,
    )
    plan_repo.save(basic_plan)

    trial_plan = Plan(
        id="plan-trial",
        tenant_id=tenant.id,
        name="Trial Tier",
        price=Money.from_str("2000.00", Currency.RUB),
        period=BillingPeriod.MONTHLY,
        included_units=50,
        overage_unit_price=Money.from_str("15.00", Currency.RUB),
        trial_days=14,
    )
    plan_repo.save(trial_plan)

    pro_plan = Plan(
        id="plan-pro",
        tenant_id=tenant.id,
        name="Pro Tier",
        price=Money.from_str("4000.00", Currency.RUB),
        period=BillingPeriod.MONTHLY,
        included_units=500,
        overage_unit_price=Money.from_str("8.00", Currency.RUB),
        trial_days=0,
    )
    plan_repo.save(pro_plan)

    return {
        "clock": clock,
        "tenant_repo": tenant_repo,
        "plan_repo": plan_repo,
        "sub_repo": sub_repo,
        "inv_repo": inv_repo,
        "usage_repo": usage_repo,
        "gateway": gateway,
        "tenant": tenant,
        "basic_plan": basic_plan,
        "trial_plan": trial_plan,
        "pro_plan": pro_plan,
    }


def test_subscribe_immediate_billing(test_env):
    use_case = SubscribeCustomerUseCase(
        tenant_repo=test_env["tenant_repo"],
        plan_repo=test_env["plan_repo"],
        subscription_repo=test_env["sub_repo"],
        invoice_repo=test_env["inv_repo"],
        payment_gateway=test_env["gateway"],
        clock=test_env["clock"],
    )

    cmd = SubscribeCustomerCommand(
        tenant_id="tenant-alpha",
        customer_id="cust-1",
        plan_id="plan-basic",
        payment_method_id="card-tok-123",
        idempotency_key="sub-cmd-001",
    )

    result = use_case.execute(cmd)

    assert result.subscription.status == SubscriptionStatus.ACTIVE
    assert result.invoice.status == InvoiceStatus.PAID
    assert result.invoice.total_amount.amount == Decimal("1000.00")
    assert test_env["gateway"].call_count == 1

    # Test idempotency: second identical call returns same result without extra charge
    result_dup = use_case.execute(cmd)
    assert result_dup.subscription.id == result.subscription.id
    assert result_dup.invoice.id == result.invoice.id
    assert test_env["gateway"].call_count == 1  # Not called again!


def test_subscribe_with_free_trial(test_env):
    use_case = SubscribeCustomerUseCase(
        tenant_repo=test_env["tenant_repo"],
        plan_repo=test_env["plan_repo"],
        subscription_repo=test_env["sub_repo"],
        invoice_repo=test_env["inv_repo"],
        payment_gateway=test_env["gateway"],
        clock=test_env["clock"],
    )

    cmd = SubscribeCustomerCommand(
        tenant_id="tenant-alpha",
        customer_id="cust-2",
        plan_id="plan-trial",
        payment_method_id="card-tok-456",
        idempotency_key="sub-cmd-trial-001",
    )

    result = use_case.execute(cmd)

    assert result.subscription.status == SubscriptionStatus.TRIALING
    assert result.subscription.trial_end == test_env["clock"].now() + timedelta(days=14)
    assert result.invoice.total_amount.amount == Decimal("0.00")
    assert test_env["gateway"].call_count == 0  # No real charge during trial initiation


def test_change_plan_with_mathematical_proration(test_env):
    # 1. Subscribe to basic plan (1000 RUB / month)
    sub_uc = SubscribeCustomerUseCase(
        tenant_repo=test_env["tenant_repo"],
        plan_repo=test_env["plan_repo"],
        subscription_repo=test_env["sub_repo"],
        invoice_repo=test_env["inv_repo"],
        payment_gateway=test_env["gateway"],
        clock=test_env["clock"],
    )
    sub_res = sub_uc.execute(
        SubscribeCustomerCommand(
            tenant_id="tenant-alpha",
            customer_id="cust-3",
            plan_id="plan-basic",
            payment_method_id="card-1",
            idempotency_key="init-sub-3",
        )
    )

    # 2. Advance time by 15 days (halfway through 30-day month)
    test_env["clock"].advance(timedelta(days=15))

    # 3. Upgrade to Pro plan (4000 RUB / month)
    change_uc = ChangePlanUseCase(
        subscription_repo=test_env["sub_repo"],
        plan_repo=test_env["plan_repo"],
        invoice_repo=test_env["inv_repo"],
        payment_gateway=test_env["gateway"],
        clock=test_env["clock"],
    )

    change_res = change_uc.execute(
        ChangePlanCommand(
            tenant_id="tenant-alpha",
            subscription_id=sub_res.subscription.id,
            new_plan_id="plan-pro",
            payment_method_id="card-1",
            idempotency_key="upgrade-sub-3",
        )
    )

    # Half month remaining:
    # Unspent credit on Basic = 500.00 RUB
    # Cost for Pro for 15 days = 2000.00 RUB
    # Net due = 1500.00 RUB
    assert change_res.proration.unspent_credit.amount == Decimal("500.00")
    assert change_res.proration.new_plan_charge.amount == Decimal("2000.00")
    assert change_res.proration.net_amount_due.amount == Decimal("1500.00")
    assert change_res.invoice.status == InvoiceStatus.PAID
    assert change_res.subscription.plan_id == "plan-pro"


def test_metered_usage_and_billing_cycle_with_overage(test_env):
    # 1. Subscribe to basic plan (100 units included, 10 RUB / overage unit)
    sub_uc = SubscribeCustomerUseCase(
        tenant_repo=test_env["tenant_repo"],
        plan_repo=test_env["plan_repo"],
        subscription_repo=test_env["sub_repo"],
        invoice_repo=test_env["inv_repo"],
        payment_gateway=test_env["gateway"],
        clock=test_env["clock"],
    )
    sub_res = sub_uc.execute(
        SubscribeCustomerCommand(
            tenant_id="tenant-alpha",
            customer_id="cust-4",
            plan_id="plan-basic",
            payment_method_id="card-1",
            idempotency_key="init-sub-4",
        )
    )

    # 2. Record 150 units of usage (50 units above included quota of 100)
    usage_uc = RecordUsageUseCase(
        subscription_repo=test_env["sub_repo"],
        usage_repo=test_env["usage_repo"],
        clock=test_env["clock"],
    )
    usage_uc.execute(
        RecordUsageCommand(
            tenant_id="tenant-alpha",
            subscription_id=sub_res.subscription.id,
            metric_name="api_calls",
            units=150,
        )
    )

    # 3. Advance clock past subscription period end
    test_env["clock"].advance(timedelta(days=31))

    # 4. Run billing cycle
    cycle_uc = RunBillingCycleUseCase(
        subscription_repo=test_env["sub_repo"],
        plan_repo=test_env["plan_repo"],
        invoice_repo=test_env["inv_repo"],
        usage_repo=test_env["usage_repo"],
        payment_gateway=test_env["gateway"],
        clock=test_env["clock"],
    )
    cycle_res = cycle_uc.execute()

    assert sub_res.subscription.id in cycle_res.renewed_subscriptions
    # Find generated invoice
    renewal_inv = test_env["inv_repo"].get_by_id(cycle_res.invoices_generated[0])
    assert renewal_inv is not None
    assert renewal_inv.status == InvoiceStatus.PAID
    # 1000 base + (50 overage * 10) = 1500 RUB
    assert renewal_inv.total_amount.amount == Decimal("1500.00")


def test_payment_failure_and_smart_retry_lifecycle(test_env):
    sub_uc = SubscribeCustomerUseCase(
        tenant_repo=test_env["tenant_repo"],
        plan_repo=test_env["plan_repo"],
        subscription_repo=test_env["sub_repo"],
        invoice_repo=test_env["inv_repo"],
        payment_gateway=test_env["gateway"],
        clock=test_env["clock"],
    )
    sub_res = sub_uc.execute(
        SubscribeCustomerCommand(
            tenant_id="tenant-alpha",
            customer_id="cust-5",
            plan_id="plan-basic",
            payment_method_id="card-1",
            idempotency_key="init-sub-5",
        )
    )

    # Simulate bank failure during renewal
    test_env["clock"].advance(timedelta(days=31))
    test_env["gateway"].simulate_declined_card = True

    cycle_uc = RunBillingCycleUseCase(
        subscription_repo=test_env["sub_repo"],
        plan_repo=test_env["plan_repo"],
        invoice_repo=test_env["inv_repo"],
        usage_repo=test_env["usage_repo"],
        payment_gateway=test_env["gateway"],
        clock=test_env["clock"],
    )
    cycle_res = cycle_uc.execute()

    assert sub_res.subscription.id in cycle_res.failed_subscriptions

    sub = test_env["sub_repo"].get_by_id(sub_res.subscription.id)
    assert sub.status == SubscriptionStatus.PAST_DUE
    assert sub.retry_count == 1
    # Customer access is revoked once past due and past period end
    assert not sub.is_access_granted(test_env["clock"].now())
