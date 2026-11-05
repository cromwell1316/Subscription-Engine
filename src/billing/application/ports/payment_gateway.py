from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from billing.domain.entities import Invoice


@dataclass(frozen=True)
class PaymentResult:
    """Outcome of attempting a payment transaction with a financial gateway."""
    success: bool
    transaction_id: Optional[str] = None
    error_message: Optional[str] = None
    is_transient: bool = False  # If True, retry may succeed (e.g., gateway timeout, rate limit)


class IPaymentGateway(ABC):
    """Abstract interface defining the contract for executing charges."""

    @abstractmethod
    def charge(
        self,
        invoice: Invoice,
        payment_method_id: str,
        idempotency_key: str,
    ) -> PaymentResult:
        """Processes payment with idempotency guarantee."""
        pass
