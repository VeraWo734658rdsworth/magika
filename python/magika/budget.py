"""Budget tracking for Magika inference — limits total bytes processed."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


class BudgetExceeded(Exception):
    """Raised when the byte budget has been exhausted."""

    def __init__(self, used: int, limit: int) -> None:
        self.used = used
        self.limit = limit
        super().__init__(f"Byte budget exceeded: used {used}, limit {limit}")


@dataclass
class BudgetPolicy:
    """Configuration for the byte-budget enforcer."""

    max_bytes: int
    reset_on_exhaustion: bool = False

    def __post_init__(self) -> None:
        if self.max_bytes <= 0:
            raise ValueError("max_bytes must be a positive integer")


@dataclass
class BudgetTracker:
    """Tracks cumulative bytes consumed against a policy."""

    policy: BudgetPolicy
    _used: int = field(default=0, init=False)

    @property
    def used(self) -> int:
        return self._used

    @property
    def remaining(self) -> int:
        return max(0, self.policy.max_bytes - self._used)

    def consume(self, n_bytes: int) -> None:
        """Record *n_bytes* consumed; raise BudgetExceeded if over limit."""
        if n_bytes < 0:
            raise ValueError("n_bytes must be non-negative")
        projected = self._used + n_bytes
        if projected > self.policy.max_bytes:
            if self.policy.reset_on_exhaustion:
                self._used = 0
            raise BudgetExceeded(projected, self.policy.max_bytes)
        self._used = projected

    def reset(self) -> None:
        """Manually reset the consumed counter to zero."""
        self._used = 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"BudgetTracker(used={self._used}, "
            f"limit={self.policy.max_bytes})"
        )
