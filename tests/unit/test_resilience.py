import time
import pytest

from billing.infrastructure.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)
from billing.infrastructure.resilience.dunning import SmartDunningPolicy


def test_circuit_breaker_transitions():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=0.1, name="test_cb")

    # Initial state is CLOSED
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True

    # 1st failure
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 1

    # 2nd failure triggers transition to OPEN
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False

    # Fast fail in OPEN state
    with pytest.raises(CircuitBreakerOpenError):
        cb.call(lambda: "should never run")

    # Wait for recovery timeout to pass
    time.sleep(0.12)

    # State transitions to HALF_OPEN
    assert cb.state == CircuitState.HALF_OPEN
    assert cb.can_execute() is True

    # Canary call succeeds -> back to CLOSED
    result = cb.call(lambda: "recovered!")
    assert result == "recovered!"
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


def test_circuit_breaker_half_open_failure_reopens():
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout_seconds=0.05, name="test_cb_fail")

    # Trip breaker
    cb.record_failure()
    assert cb.state == CircuitState.OPEN

    # Wait for recovery timeout
    time.sleep(0.06)
    assert cb.state == CircuitState.HALF_OPEN

    # Canary call fails -> immediately returns to OPEN
    def failing_canary():
        raise ConnectionResetError("Bank connection failed")

    with pytest.raises(ConnectionResetError):
        cb.call(failing_canary)

    assert cb.state == CircuitState.OPEN


def test_smart_dunning_policy_backoff():
    policy = SmartDunningPolicy(base_interval_hours=2.0, backoff_multiplier=2.0, max_interval_hours=24.0)

    # Attempt 0: ~2.0 hours (+ jitter)
    # Attempt 1: ~4.0 hours (+ jitter)
    # Attempt 2: ~8.0 hours (+ jitter)
    from datetime import datetime, timezone
    now = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)

    next_0 = policy.calculate_next_retry(0, now)
    diff_0 = (next_0 - now).total_seconds() / 3600.0
    assert 2.0 <= diff_0 <= 2.3

    next_1 = policy.calculate_next_retry(1, now)
    diff_1 = (next_1 - now).total_seconds() / 3600.0
    assert 4.0 <= diff_1 <= 4.5

    assert policy.should_retry(0, is_transient=True) is True
    assert policy.should_retry(3, is_transient=True) is False  # Max attempts reached
