from dataclasses import dataclass
import uuid

from billing.application.ports.clock import IClock
from billing.application.ports.repositories import ISubscriptionRepository, IUsageRepository
from billing.domain.entities import UsageRecord
from billing.domain.exceptions import SubscriptionNotActiveError, TenantMismatchError


@dataclass(frozen=True)
class RecordUsageCommand:
    tenant_id: str
    subscription_id: str
    metric_name: str
    units: int


class RecordUsageUseCase:
    """Records metered usage event consumed by an active subscription."""

    def __init__(
        self,
        subscription_repo: ISubscriptionRepository,
        usage_repo: IUsageRepository,
        clock: IClock,
    ) -> None:
        self.subscription_repo = subscription_repo
        self.usage_repo = usage_repo
        self.clock = clock

    def execute(self, cmd: RecordUsageCommand) -> UsageRecord:
        sub = self.subscription_repo.get_by_id(cmd.subscription_id)
        if not sub or sub.tenant_id != cmd.tenant_id:
            raise TenantMismatchError(f"Subscription {cmd.subscription_id} not found for tenant")

        now = self.clock.now()
        if not sub.is_access_granted(now):
            raise SubscriptionNotActiveError("Cannot record usage for expired or inactive subscription")

        record = UsageRecord(
            id=str(uuid.uuid4()),
            tenant_id=cmd.tenant_id,
            customer_id=sub.customer_id,
            subscription_id=sub.id,
            units=cmd.units,
            recorded_at=now,
        )
        self.usage_repo.record(record)
        return record
