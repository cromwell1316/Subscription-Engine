from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

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
    ProrationResult,
    SubscriptionStatus,
)


@dataclass
class Tenant:
    """Represents an isolated organization (tenant) on the platform."""
    id: str
    name: str
    currency: Currency
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

    def deactivate(self) -> None:
        self.is_active = False


@dataclass
class Plan:
    """Tariff plan configured by a tenant."""
    id: str
    tenant_id: str
    name: str
    price: Money
    period: BillingPeriod
    included_units: int = 0
    overage_unit_price: Optional[Money] = None
    trial_days: int = 0
    is_active: bool = True
    version: int = 1

    def __post_init__(self) -> None:
        if self.price.is_negative():
            raise InvalidMoneyOperationError("Plan price cannot be negative")
        if self.trial_days < 0:
            raise InvalidMoneyOperationError("Trial days cannot be negative")
        if self.overage_unit_price is None:
            self.overage_unit_price = Money.zero(self.price.currency)
        elif self.overage_unit_price.currency != self.price.currency:
            raise CurrencyMismatchError("Overage price currency must match plan price currency")

    def deactivate(self) -> None:
        self.is_active = False


@dataclass
class InvoiceLineItem:
    """Single line item within a billing invoice."""
    description: str
    amount: Money
    quantity: int = 1

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvalidMoneyOperationError("Line item quantity must be greater than zero")

    @property
    def total(self) -> Money:
        return self.amount * self.quantity


@dataclass
class Invoice:
    """Payment invoice representing a financial demand."""
    id: str
    tenant_id: str
    customer_id: str
    subscription_id: Optional[str]
    currency: Currency
    status: InvoiceStatus = InvoiceStatus.DRAFT
    line_items: List[InvoiceLineItem] = field(default_factory=list)
    idempotency_key: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    failure_reason: Optional[str] = None

    @property
    def total_amount(self) -> Money:
        total = Money.zero(self.currency)
        for item in self.line_items:
            total = total + item.total
        return total

    def add_item(self, description: str, amount: Money, quantity: int = 1) -> None:
        if self.status != InvoiceStatus.DRAFT:
            raise InvalidStateTransitionError("Cannot add line items to a finalized invoice")
        if amount.currency != self.currency:
            raise CurrencyMismatchError("Line item currency must match invoice currency")
        self.line_items.append(InvoiceLineItem(description=description, amount=amount, quantity=quantity))

    def issue(self, due_date: datetime) -> None:
        if self.status != InvoiceStatus.DRAFT:
            raise InvalidStateTransitionError(f"Cannot issue invoice from status {self.status.value}")
        if not self.line_items:
            raise InvalidMoneyOperationError("Cannot issue an empty invoice")
        self.status = InvoiceStatus.PENDING
        self.due_date = due_date

    def mark_paid(self, paid_at: datetime) -> None:
        if self.status not in (InvoiceStatus.PENDING, InvoiceStatus.FAILED):
            raise InvalidStateTransitionError(f"Cannot mark invoice as paid from status {self.status.value}")
        self.status = InvoiceStatus.PAID
        self.paid_at = paid_at
        self.failure_reason = None

    def mark_failed(self, reason: str) -> None:
        if self.status != InvoiceStatus.PENDING:
            raise InvalidStateTransitionError(f"Cannot fail invoice from status {self.status.value}")
        self.status = InvoiceStatus.FAILED
        self.failure_reason = reason

    def void(self) -> None:
        if self.status == InvoiceStatus.PAID:
            raise InvalidStateTransitionError("Cannot void an already paid invoice")
        self.status = InvoiceStatus.VOID


@dataclass
class Subscription:
    """Subscription contract binding a customer to a tariff plan."""
    id: str
    tenant_id: str
    customer_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    retry_count: int = 0

    def is_access_granted(self, at_time: datetime) -> bool:
        """Determines if the customer should be given service access."""
        if self.status == SubscriptionStatus.ACTIVE:
            return at_time <= self.current_period_end
        if self.status == SubscriptionStatus.TRIALING:
            return self.trial_end is not None and at_time <= self.trial_end
        return False

    def activate(self, period_start: datetime, period_end: datetime) -> None:
        if self.status not in (SubscriptionStatus.TRIALING, SubscriptionStatus.PAST_DUE, SubscriptionStatus.PAUSED):
            # allow initial activation
            pass
        self.status = SubscriptionStatus.ACTIVE
        self.current_period_start = period_start
        self.current_period_end = period_end
        self.retry_count = 0

    def mark_past_due(self) -> None:
        if self.status == SubscriptionStatus.CANCELED:
            raise InvalidStateTransitionError("Cannot mark a canceled subscription as past due")
        self.status = SubscriptionStatus.PAST_DUE
        self.retry_count += 1

    def pause(self) -> None:
        if self.status == SubscriptionStatus.CANCELED:
            raise InvalidStateTransitionError("Cannot pause a canceled subscription")
        self.status = SubscriptionStatus.PAUSED

    def resume(self) -> None:
        if self.status != SubscriptionStatus.PAUSED:
            raise InvalidStateTransitionError("Can only resume a paused subscription")
        self.status = SubscriptionStatus.ACTIVE

    def cancel(self, immediate: bool = False) -> None:
        if self.status == SubscriptionStatus.CANCELED:
            return
        if immediate:
            self.status = SubscriptionStatus.CANCELED
            self.cancel_at_period_end = False
        else:
            self.cancel_at_period_end = True

    def calculate_proration(
        self,
        current_plan: Plan,
        new_plan: Plan,
        at_time: datetime,
    ) -> ProrationResult:
        """Calculates mathematical proration when changing plans mid-period."""
        if current_plan.tenant_id != new_plan.tenant_id or current_plan.tenant_id != self.tenant_id:
            raise TenantMismatchError("Cannot calculate proration across different tenants")
        if current_plan.price.currency != new_plan.price.currency:
            raise CurrencyMismatchError("Cannot prorate across plans with different currencies")

        currency = current_plan.price.currency
        total_seconds = (self.current_period_end - self.current_period_start).total_seconds()
        if total_seconds <= 0:
            return ProrationResult(
                unspent_credit=Money.zero(currency),
                new_plan_charge=new_plan.price,
                net_amount_due=new_plan.price,
                remaining_days=0,
                total_period_days=0,
            )

        remaining_seconds = max(0.0, (self.current_period_end - at_time).total_seconds())
        ratio = Decimal(str(remaining_seconds / total_seconds))

        unspent_credit = (current_plan.price * ratio)
        new_plan_charge = (new_plan.price * ratio)

        if new_plan_charge >= unspent_credit:
            net_amount_due = new_plan_charge - unspent_credit
        else:
            net_amount_due = Money.zero(currency)

        remaining_days = int(remaining_seconds // 86400)
        total_days = max(1, int(total_seconds // 86400))

        return ProrationResult(
            unspent_credit=unspent_credit,
            new_plan_charge=new_plan_charge,
            net_amount_due=net_amount_due,
            remaining_days=remaining_days,
            total_period_days=total_days,
        )

    def apply_plan_change(self, new_plan_id: str) -> None:
        self.plan_id = new_plan_id


@dataclass
class UsageRecord:
    """Metered usage event consumed by a customer."""
    id: str
    tenant_id: str
    customer_id: str
    subscription_id: str
    units: int
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.units <= 0:
            raise InvalidMoneyOperationError("Usage units must be strictly positive")
