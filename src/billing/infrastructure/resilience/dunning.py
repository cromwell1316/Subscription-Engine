from datetime import datetime, timedelta, timezone
import random


class SmartDunningPolicy:
    """
    Computes intelligent retry intervals for failed recurring charges using
    exponential backoff with randomized jitter to prevent thundering herd problems.
    """

    def __init__(
        self,
        base_interval_hours: float = 4.0,
        backoff_multiplier: float = 2.0,
        max_interval_hours: float = 72.0,
        max_attempts: int = 3,
    ) -> None:
        self.base_interval_hours = base_interval_hours
        self.backoff_multiplier = backoff_multiplier
        self.max_interval_hours = max_interval_hours
        self.max_attempts = max_attempts

    def should_retry(self, current_attempt: int, is_transient: bool) -> bool:
        if current_attempt >= self.max_attempts:
            return False
        # If the card is permanently declined or lost, do not retry blindly
        return is_transient or current_attempt < 2

    def calculate_next_retry(self, current_attempt: int, from_time: datetime) -> datetime:
        """Calculates the scheduled timestamp for the next dunning attempt."""
        # Exponential backoff: base * (multiplier ^ attempt)
        hours = self.base_interval_hours * (self.backoff_multiplier ** current_attempt)
        hours = min(hours, self.max_interval_hours)

        # Add 10% randomized jitter
        jitter_hours = hours * random.uniform(0.0, 0.1)
        total_hours = hours + jitter_hours

        return from_time + timedelta(hours=total_hours)
