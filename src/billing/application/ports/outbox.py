from abc import ABC, abstractmethod
from typing import List

from billing.domain.events import DomainEvent


class IOutboxRepository(ABC):
    """Abstract port for persisting domain events within transactional boundaries."""

    @abstractmethod
    def save_event(self, event: DomainEvent) -> None:
        """Persists an event to the outbox table inside the current transaction."""
        pass

    @abstractmethod
    def list_unpublished(self, limit: int = 50) -> List[DomainEvent]:
        """Retrieves unpublished pending domain events."""
        pass

    @abstractmethod
    def mark_published(self, event_id: str) -> None:
        """Marks the event as successfully dispatched to external consumers."""
        pass
