"""Domain exceptions for Billing and Subscription platform."""


class BillingDomainError(Exception):
    """Base exception for all domain-level billing errors."""
    pass


class InvalidMoneyOperationError(BillingDomainError):
    """Raised when an invalid operation is performed on Money (e.g., currency mismatch, negative amount)."""
    pass


class InvalidStateTransitionError(BillingDomainError):
    """Raised when an entity attempts an illegal state transition."""
    pass


class TenantMismatchError(BillingDomainError):
    """Raised when attempting an operation across different tenants."""
    pass


class PlanInactiveError(BillingDomainError):
    """Raised when attempting to subscribe to an inactive plan."""
    pass


class SubscriptionNotActiveError(BillingDomainError):
    """Raised when an operation requires an active subscription but it is in a different state."""
    pass


class DuplicateOperationError(BillingDomainError):
    """Raised when an operation with the same idempotency key was already completed."""
    pass


class CurrencyMismatchError(BillingDomainError):
    """Raised when currencies do not match in a multi-currency operation."""
    pass
