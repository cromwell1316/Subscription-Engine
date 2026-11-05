from datetime import datetime, timezone
from enum import Enum
import threading
from typing import Callable, TypeVar

T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "CLOSED"      # Normal operation: traffic flows through
    OPEN = "OPEN"          # Failing fast: downstream service is down, blocking traffic
    HALF_OPEN = "HALF_OPEN"  # Testing downstream recovery with canary calls


class CircuitBreakerOpenError(Exception):
    """Raised when an operation is attempted while the circuit breaker is in OPEN state."""
    pass


class CircuitBreaker:
    """
    Implements the Circuit Breaker pattern to protect the system from cascading failures
    when external dependencies (payment gateways, banks) experience downtime or timeouts.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 15.0,
        name: str = "payment_gateway",
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.name = name

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_state_change = datetime.now(timezone.utc)
        self._lock = threading.Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            self._evaluate_state()
            return self._state

    @property
    def failure_count(self) -> int:
        with self._lock:
            return self._failure_count

    def _evaluate_state(self) -> None:
        """Transitions from OPEN to HALF_OPEN once recovery timeout elapses."""
        if self._state == CircuitState.OPEN:
            elapsed = (datetime.now(timezone.utc) - self._last_state_change).total_seconds()
            if elapsed >= self.recovery_timeout_seconds:
                self._state = CircuitState.HALF_OPEN
                self._last_state_change = datetime.now(timezone.utc)

    def can_execute(self) -> bool:
        with self._lock:
            self._evaluate_state()
            return self._state != CircuitState.OPEN

    def record_success(self) -> None:
        with self._lock:
            self._failure_count = 0
            if self._state != CircuitState.CLOSED:
                self._state = CircuitState.CLOSED
                self._last_state_change = datetime.now(timezone.utc)

    def record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold or self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                self._last_state_change = datetime.now(timezone.utc)

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Executes the function under the protection of the circuit breaker."""
        if not self.can_execute():
            raise CircuitBreakerOpenError(
                f"Circuit breaker '{self.name}' is OPEN. Fast-failing to protect downstream service."
            )

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception:
            self.record_failure()
            raise
