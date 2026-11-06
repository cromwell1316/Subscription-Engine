from functools import lru_cache
from decimal import Decimal

from billing.application.ports.clock import IClock, SystemClock
from billing.application.ports.payment_gateway import IPaymentGateway
from billing.application.ports.repositories import (
    IInvoiceRepository,
    IPlanRepository,
    ISubscriptionRepository,
    ITenantRepository,
    IUsageRepository,
)
from billing.application.use_cases.change_plan import ChangePlanUseCase
from billing.application.use_cases.record_usage import RecordUsageCommand, RecordUsageUseCase
from billing.application.use_cases.run_billing_cycle import RunBillingCycleUseCase
from billing.application.use_cases.subscribe_customer import (
    SubscribeCustomerCommand,
    SubscribeCustomerUseCase,
)
from billing.domain.entities import Plan, Tenant
from billing.domain.value_objects import BillingPeriod, Currency, Money
from billing.infrastructure.gateways.fault_tolerant_gateway import (
    FaultTolerantPaymentGatewayEmulator,
)
from billing.infrastructure.persistence.in_memory_repositories import (
    InMemoryInvoiceRepository,
    InMemoryOutboxRepository,
    InMemoryPlanRepository,
    InMemorySubscriptionRepository,
    InMemoryTenantRepository,
    InMemoryUsageRepository,
)
from billing.infrastructure.resilience.circuit_breaker import CircuitBreaker


class ServiceContainer:
    """Application services and repositories container."""

    def __init__(self) -> None:
        self.clock: IClock = SystemClock()
        self.tenant_repo: ITenantRepository = InMemoryTenantRepository()
        self.plan_repo: IPlanRepository = InMemoryPlanRepository()
        self.subscription_repo: ISubscriptionRepository = InMemorySubscriptionRepository()
        self.invoice_repo: IInvoiceRepository = InMemoryInvoiceRepository()
        self.usage_repo: IUsageRepository = InMemoryUsageRepository()
        self.outbox_repo: InMemoryOutboxRepository = InMemoryOutboxRepository()
        self.payment_gateway: FaultTolerantPaymentGatewayEmulator = FaultTolerantPaymentGatewayEmulator()
        self.circuit_breaker: CircuitBreaker = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=15.0, name="payment_gateway")
        self.seed_demo_data()

    def seed_demo_data(self) -> None:
        """Pre-seeds demonstration tenant and plans if repository is empty."""
        if self.tenant_repo.list_all():
            return

        tenant = Tenant(id="tenant-demo", name="Acme Cloud Platform", currency=Currency.RUB)
        self.tenant_repo.save(tenant)

        plan_basic = Plan(
            id="plan-basic",
            tenant_id=tenant.id,
            name="Стартовый тариф",
            price=Money.from_str("1500.00", Currency.RUB),
            period=BillingPeriod.MONTHLY,
            included_units=100,
            overage_unit_price=Money.from_str("10.00", Currency.RUB),
            trial_days=0,
        )
        plan_pro = Plan(
            id="plan-pro",
            tenant_id=tenant.id,
            name="Профессиональный",
            price=Money.from_str("4500.00", Currency.RUB),
            period=BillingPeriod.MONTHLY,
            included_units=500,
            overage_unit_price=Money.from_str("6.00", Currency.RUB),
            trial_days=0,
        )
        plan_trial = Plan(
            id="plan-trial",
            tenant_id=tenant.id,
            name="Корпоративный (Триал)",
            price=Money.from_str("12000.00", Currency.RUB),
            period=BillingPeriod.MONTHLY,
            included_units=2000,
            overage_unit_price=Money.from_str("4.00", Currency.RUB),
            trial_days=14,
        )
        self.plan_repo.save(plan_basic)
        self.plan_repo.save(plan_pro)
        self.plan_repo.save(plan_trial)

        # Seed initial customers and usage
        sub_uc = self.get_subscribe_use_case()
        usage_uc = self.get_record_usage_use_case()

        res1 = sub_uc.execute(
            SubscribeCustomerCommand(
                tenant_id=tenant.id,
                customer_id="cust-demo-101",
                plan_id=plan_basic.id,
                payment_method_id="card-4242",
                idempotency_key="seed-sub-101",
            )
        )
        usage_uc.execute(
            RecordUsageCommand(
                tenant_id=tenant.id,
                subscription_id=res1.subscription.id,
                metric_name="api_calls",
                units=65,
            )
        )

        res2 = sub_uc.execute(
            SubscribeCustomerCommand(
                tenant_id=tenant.id,
                customer_id="cust-enterprise-303",
                plan_id=plan_pro.id,
                payment_method_id="card-9999",
                idempotency_key="seed-sub-303",
            )
        )
        usage_uc.execute(
            RecordUsageCommand(
                tenant_id=tenant.id,
                subscription_id=res2.subscription.id,
                metric_name="api_calls",
                units=380,
            )
        )

    def get_system_stats(self) -> dict:
        tenants = self.tenant_repo.list_all()
        plans_count = sum(len(self.plan_repo.list_by_tenant(t.id)) for t in tenants)
        all_subs = self.subscription_repo.list_due_for_renewal(self.clock.now() + self.clock.now().resolution * 100000)
        # Fallback to internal list for in-memory
        if hasattr(self.subscription_repo, "_subs"):
            subs = list(self.subscription_repo._subs.values())
        else:
            subs = all_subs

        if hasattr(self.invoice_repo, "_invoices"):
            invoices = list(self.invoice_repo._invoices.values())
        else:
            invoices = []

        paid_revenue = sum(
            (inv.total_amount.amount for inv in invoices if inv.status.value == "PAID"),
            Decimal("0.00"),
        )

        return {
            "tenants_count": len(tenants),
            "plans_count": plans_count,
            "subscriptions_count": len(subs),
            "invoices_count": len(invoices),
            "total_revenue": str(paid_revenue),
            "circuit_breaker": {
                "state": self.circuit_breaker.state.value,
                "failure_count": self.circuit_breaker.failure_count,
                "threshold": self.circuit_breaker.failure_threshold,
                "recovery_timeout": self.circuit_breaker.recovery_timeout_seconds,
                "is_simulating_outage": self.payment_gateway.simulate_transient_failure,
            },
        }

    def get_subscribe_use_case(self) -> SubscribeCustomerUseCase:
        return SubscribeCustomerUseCase(
            tenant_repo=self.tenant_repo,
            plan_repo=self.plan_repo,
            subscription_repo=self.subscription_repo,
            invoice_repo=self.invoice_repo,
            payment_gateway=self.payment_gateway,
            clock=self.clock,
        )

    def get_change_plan_use_case(self) -> ChangePlanUseCase:
        return ChangePlanUseCase(
            subscription_repo=self.subscription_repo,
            plan_repo=self.plan_repo,
            invoice_repo=self.invoice_repo,
            payment_gateway=self.payment_gateway,
            clock=self.clock,
        )

    def get_record_usage_use_case(self) -> RecordUsageUseCase:
        return RecordUsageUseCase(
            subscription_repo=self.subscription_repo,
            usage_repo=self.usage_repo,
            clock=self.clock,
        )

    def get_run_billing_cycle_use_case(self) -> RunBillingCycleUseCase:
        return RunBillingCycleUseCase(
            subscription_repo=self.subscription_repo,
            plan_repo=self.plan_repo,
            invoice_repo=self.invoice_repo,
            usage_repo=self.usage_repo,
            payment_gateway=self.payment_gateway,
            clock=self.clock,
        )


@lru_cache(maxsize=1)
def get_container() -> ServiceContainer:
    """Returns singleton instance of application service container."""
    return ServiceContainer()
