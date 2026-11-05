from functools import lru_cache

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
from billing.application.use_cases.record_usage import RecordUsageUseCase
from billing.application.use_cases.run_billing_cycle import RunBillingCycleUseCase
from billing.application.use_cases.subscribe_customer import SubscribeCustomerUseCase
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


class ServiceContainer:
    """Application services and repositories container."""

    def __init__(self) -> None:
        self.clock: IClock = SystemClock()
        self.tenant_repo: ITenantRepository = InMemoryTenantRepository()
        self.plan_repo: IPlanRepository = InMemoryPlanRepository()
        self.subscription_repo: ISubscriptionRepository = InMemorySubscriptionRepository()
        self.invoice_repo: IInvoiceRepository = InMemoryInvoiceRepository()
        self.usage_repo: IUsageRepository = InMemoryUsageRepository()
        self.payment_gateway: IPaymentGateway = FaultTolerantPaymentGatewayEmulator()

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
