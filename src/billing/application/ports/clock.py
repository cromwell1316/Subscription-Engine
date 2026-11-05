from abc import ABC, abstractmethod
from datetime import datetime, timezone


class IClock(ABC):
    """Time provider interface allowing deterministic time control during testing."""

    @abstractmethod
    def now(self) -> datetime:
        pass


class SystemClock(IClock):
    """Default system wall-clock provider."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FrozenClock(IClock):
    """Test clock that can be frozen or advanced programmatically."""

    def __init__(self, fixed_time: datetime) -> None:
        self._current_time = fixed_time

    def now(self) -> datetime:
        return self._current_time

    def set_time(self, new_time: datetime) -> None:
        self._current_time = new_time

    def advance(self, duration) -> None:
        self._current_time += duration
