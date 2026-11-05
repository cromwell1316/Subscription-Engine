from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from billing.domain.entities import Invoice, Plan, Subscription, Tenant, UsageRecord


class ITenantRepository(ABC):
    @abstractmethod
    def save(self, tenant: Tenant) -> None:
        pass

    @abstractmethod
    def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        pass

    @abstractmethod
    def list_all(self) -> List[Tenant]:
        pass


class IPlanRepository(ABC):
    @abstractmethod
    def save(self, plan: Plan) -> None:
        pass

    @abstractmethod
    def get_by_id(self, plan_id: str) -> Optional[Plan]:
        pass

    @abstractmethod
    def list_by_tenant(self, tenant_id: str) -> List[Plan]:
        pass


class ISubscriptionRepository(ABC):
    @abstractmethod
    def save(self, subscription: Subscription) -> None:
        pass

    @abstractmethod
    def get_by_id(self, subscription_id: str) -> Optional[Subscription]:
        pass

    @abstractmethod
    def list_by_customer(self, tenant_id: str, customer_id: str) -> List[Subscription]:
        pass

    @abstractmethod
    def list_due_for_renewal(self, as_of: datetime) -> List[Subscription]:
        pass


class IInvoiceRepository(ABC):
    @abstractmethod
    def save(self, invoice: Invoice) -> None:
        pass

    @abstractmethod
    def get_by_id(self, invoice_id: str) -> Optional[Invoice]:
        pass

    @abstractmethod
    def get_by_idempotency_key(self, tenant_id: str, key: str) -> Optional[Invoice]:
        pass

    @abstractmethod
    def list_by_subscription(self, subscription_id: str) -> List[Invoice]:
        pass


class IUsageRepository(ABC):
    @abstractmethod
    def record(self, record: UsageRecord) -> None:
        pass

    @abstractmethod
    def get_total_units(
        self,
        tenant_id: str,
        subscription_id: str,
        start_time: datetime,
        end_time: datetime,
    ) -> int:
        pass
