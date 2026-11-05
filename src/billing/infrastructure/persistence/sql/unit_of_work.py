from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session, sessionmaker

from billing.infrastructure.persistence.sql.repositories import (
    SqlAlchemyInvoiceRepository,
    SqlAlchemyOutboxRepository,
    SqlAlchemyPlanRepository,
    SqlAlchemySubscriptionRepository,
    SqlAlchemyTenantRepository,
    SqlAlchemyUsageRepository,
)


class IUnitOfWork(ABC):
    """Abstract Unit of Work contract ensuring ACID guarantees across domain operations."""

    tenants: SqlAlchemyTenantRepository
    plans: SqlAlchemyPlanRepository
    subscriptions: SqlAlchemySubscriptionRepository
    invoices: SqlAlchemyInvoiceRepository
    usage: SqlAlchemyUsageRepository
    outbox: SqlAlchemyOutboxRepository

    @abstractmethod
    def __enter__(self) -> "IUnitOfWork":
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy Unit of Work implementation managing transactional lifecycle."""

    def __init__(self, session_factory: sessionmaker) -> None:
        self.session_factory = session_factory
        self.session: Optional[Session] = None

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self.session_factory()
        self.tenants = SqlAlchemyTenantRepository(self.session)
        self.plans = SqlAlchemyPlanRepository(self.session)
        self.subscriptions = SqlAlchemySubscriptionRepository(self.session)
        self.invoices = SqlAlchemyInvoiceRepository(self.session)
        self.usage = SqlAlchemyUsageRepository(self.session)
        self.outbox = SqlAlchemyOutboxRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session is not None:
            if exc_type is not None:
                self.rollback()
            self.session.close()

    def commit(self) -> None:
        if self.session is not None:
            self.session.commit()

    def rollback(self) -> None:
        if self.session is not None:
            self.session.rollback()
