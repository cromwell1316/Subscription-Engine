from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
import uuid


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events emitted by the billing engine."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: str = ""

    @property
    def event_type(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class SubscriptionCreatedEvent(DomainEvent):
    subscription_id: str = ""
    customer_id: str = ""
    plan_id: str = ""
    is_trial: bool = False


@dataclass(frozen=True)
class SubscriptionActivatedEvent(DomainEvent):
    subscription_id: str = ""
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


@dataclass(frozen=True)
class PlanUpgradedEvent(DomainEvent):
    subscription_id: str = ""
    old_plan_id: str = ""
    new_plan_id: str = ""
    net_amount_due: Decimal = Decimal("0.00")
    unspent_credit: Decimal = Decimal("0.00")


@dataclass(frozen=True)
class PaymentFailedEvent(DomainEvent):
    invoice_id: str = ""
    subscription_id: Optional[str] = None
    reason: str = ""
    is_transient: bool = False
    retry_count: int = 0


@dataclass(frozen=True)
class InvoicePaidEvent(DomainEvent):
    invoice_id: str = ""
    subscription_id: Optional[str] = None
    total_amount: Decimal = Decimal("0.00")
    transaction_id: str = ""


@dataclass(frozen=True)
class OverageDetectedEvent(DomainEvent):
    subscription_id: str = ""
    units_consumed: int = 0
    quota_included: int = 0
    overage_units: int = 0
    overage_charge: Decimal = Decimal("0.00")
