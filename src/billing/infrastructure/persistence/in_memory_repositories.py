from datetime import datetime
from typing import Dict, List, Optional

from billing.application.ports.outbox import IOutboxRepository
from billing.application.ports.repositories import (
    IInvoiceRepository,
    IPlanRepository,
    ISubscriptionRepository,
    ITenantRepository,
    IUsageRepository,
)
from billing.domain.entities import Invoice, Plan, Subscription, Tenant, UsageRecord
from billing.domain.events import DomainEvent


class InMemoryTenantRepository(ITenantRepository):
    def __init__(self) -> None:
        self._tenants: Dict[str, Tenant] = {}

    def save(self, tenant: Tenant) -> None:
        self._tenants[tenant.id] = tenant

    def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        return self._tenants.get(tenant_id)

    def list_all(self) -> List[Tenant]:
        return list(self._tenants.values())


class InMemoryPlanRepository(IPlanRepository):
    def __init__(self) -> None:
        self._plans: Dict[str, Plan] = {}

    def save(self, plan: Plan) -> None:
        self._plans[plan.id] = plan

    def get_by_id(self, plan_id: str) -> Optional[Plan]:
        return self._plans.get(plan_id)

    def list_by_tenant(self, tenant_id: str) -> List[Plan]:
        return [p for p in self._plans.values() if p.tenant_id == tenant_id]


class InMemorySubscriptionRepository(ISubscriptionRepository):
    def __init__(self) -> None:
        self._subs: Dict[str, Subscription] = {}

    def save(self, subscription: Subscription) -> None:
        self._subs[subscription.id] = subscription

    def get_by_id(self, subscription_id: str) -> Optional[Subscription]:
        return self._subs.get(subscription_id)

    def list_by_customer(self, tenant_id: str, customer_id: str) -> List[Subscription]:
        return [
            s for s in self._subs.values()
            if s.tenant_id == tenant_id and s.customer_id == customer_id
        ]

    def list_due_for_renewal(self, as_of: datetime) -> List[Subscription]:
        return [
            s for s in self._subs.values()
            if s.current_period_end <= as_of
        ]


class InMemoryInvoiceRepository(IInvoiceRepository):
    def __init__(self) -> None:
        self._invoices: Dict[str, Invoice] = {}

    def save(self, invoice: Invoice) -> None:
        self._invoices[invoice.id] = invoice

    def get_by_id(self, invoice_id: str) -> Optional[Invoice]:
        return self._invoices.get(invoice_id)

    def get_by_idempotency_key(self, tenant_id: str, key: str) -> Optional[Invoice]:
        for inv in self._invoices.values():
            if inv.tenant_id == tenant_id and inv.idempotency_key == key:
                return inv
        return None

    def list_by_subscription(self, subscription_id: str) -> List[Invoice]:
        return [inv for inv in self._invoices.values() if inv.subscription_id == subscription_id]


class InMemoryUsageRepository(IUsageRepository):
    def __init__(self) -> None:
        self._records: List[UsageRecord] = []

    def record(self, record: UsageRecord) -> None:
        self._records.append(record)

    def get_total_units(
        self,
        tenant_id: str,
        subscription_id: str,
        start_time: datetime,
        end_time: datetime,
    ) -> int:
        total = 0
        for r in self._records:
            if (
                r.tenant_id == tenant_id
                and r.subscription_id == subscription_id
                and start_time <= r.recorded_at <= end_time
            ):
                total += r.units
        return total


class InMemoryOutboxRepository(IOutboxRepository):
    def __init__(self) -> None:
        self._events: List[DomainEvent] = []
        self._published: set = set()

    def save_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def list_unpublished(self, limit: int = 50) -> List[DomainEvent]:
        return [e for e in self._events if e.event_id not in self._published][:limit]

    def mark_published(self, event_id: str) -> None:
        self._published.add(event_id)

    def list_all(self) -> List[DomainEvent]:
        return list(reversed(self._events))
