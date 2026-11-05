from typing import Dict, Optional
import uuid

from billing.application.ports.payment_gateway import IPaymentGateway, PaymentResult
from billing.domain.entities import Invoice


class FaultTolerantPaymentGatewayEmulator(IPaymentGateway):
    """
    Testable payment gateway emulator designed to simulate network failures,
    transient timeouts, card declines, and guarantee strict idempotency.
    """

    def __init__(self) -> None:
        self._processed_transactions: Dict[str, PaymentResult] = {}
        self.simulate_transient_failure: bool = False
        self.simulate_declined_card: bool = False
        self.call_count: int = 0

    def charge(
        self,
        invoice: Invoice,
        payment_method_id: str,
        idempotency_key: str,
    ) -> PaymentResult:
        self.call_count += 1

        # Strict idempotency guarantee: repeated request returns exact previous result
        if idempotency_key in self._processed_transactions:
            return self._processed_transactions[idempotency_key]

        if self.simulate_transient_failure:
            result = PaymentResult(
                success=False,
                error_message="Gateway timeout / 504 Gateway Unavailable",
                is_transient=True,
            )
            # Transient failures may not be cached as final or can be retried
            return result

        if self.simulate_declined_card:
            result = PaymentResult(
                success=False,
                error_message="Card declined: Insufficient funds",
                is_transient=False,
            )
            self._processed_transactions[idempotency_key] = result
            return result

        # Successful transaction
        tx_id = f"tx_{uuid.uuid4().hex[:12]}"
        result = PaymentResult(
            success=True,
            transaction_id=tx_id,
        )
        self._processed_transactions[idempotency_key] = result
        return result
