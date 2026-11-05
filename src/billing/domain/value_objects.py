from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Union

from billing.domain.exceptions import CurrencyMismatchError, InvalidMoneyOperationError


class Currency(str, Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class BillingPeriod(str, Enum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

    @property
    def approx_days(self) -> int:
        if self == BillingPeriod.MONTHLY:
            return 30
        elif self == BillingPeriod.YEARLY:
            return 365
        return 30


class SubscriptionStatus(str, Enum):
    TRIALING = "TRIALING"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    PAUSED = "PAUSED"
    CANCELED = "CANCELED"


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    VOID = "VOID"


@dataclass(frozen=True)
class Money:
    """Immutable monetary representation ensuring precision and currency safety."""
    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))
        # Quantize to 2 decimal places standard
        quantized = self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        object.__setattr__(self, "amount", quantized)

    @classmethod
    def zero(cls, currency: Currency) -> Money:
        return cls(amount=Decimal("0.00"), currency=currency)

    @classmethod
    def from_str(cls, amount_str: str, currency: Currency) -> Money:
        return cls(amount=Decimal(amount_str), currency=currency)

    def _ensure_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise CurrencyMismatchError(
                f"Cannot operate between {self.currency.value} and {other.currency.value}"
            )

    def add(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def sub(self, other: Money) -> Money:
        self._ensure_same_currency(other)
        return Money(amount=self.amount - other.amount, currency=self.currency)

    def mul(self, factor: Union[int, float, Decimal]) -> Money:
        if isinstance(factor, (int, float)):
            factor = Decimal(str(factor))
        return Money(amount=self.amount * factor, currency=self.currency)

    def is_positive(self) -> bool:
        return self.amount > Decimal("0.00")

    def is_zero(self) -> bool:
        return self.amount == Decimal("0.00")

    def is_negative(self) -> bool:
        return self.amount < Decimal("0.00")

    def __add__(self, other: Money) -> Money:
        return self.add(other)

    def __sub__(self, other: Money) -> Money:
        return self.sub(other)

    def __mul__(self, factor: Union[int, float, Decimal]) -> Money:
        return self.mul(factor)

    def __lt__(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: Money) -> bool:
        self._ensure_same_currency(other)
        return self.amount >= other.amount

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency.value}"


@dataclass(frozen=True)
class IdempotencyKey:
    """Unique key ensuring exactly-once processing of financial operations."""
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise InvalidMoneyOperationError("Idempotency key cannot be empty")


@dataclass(frozen=True)
class ProrationResult:
    """Result of proportional plan upgrade/downgrade calculation."""
    unspent_credit: Money
    new_plan_charge: Money
    net_amount_due: Money
    remaining_days: int
    total_period_days: int
