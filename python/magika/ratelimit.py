"""Rate limiting for Magika identification calls."""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field


class RateLimitExceeded(Exception):
    """Raised when the rate limit is exceeded."""

    def __init__(self, limit: int, window: float) -> None:
        self.limit = limit
        self.window = window
        super().__init__(
            f"Rate limit of {limit} requests per {window}s exceeded"
        )


@dataclass
class RateLimitPolicy:
    max_calls: int = 100
    window_seconds: float = 1.0

    def __post_init__(self) -> None:
        if self.max_calls <= 0:
            raise ValueError("max_calls must be positive")
        if self.window_seconds <= 0:
            raise ValueError("window_seconds must be positive")


class RateLimiter:
    """Sliding-window rate limiter."""

    def __init__(self, policy: RateLimitPolicy) -> None:
        self._policy = policy
        self._timestamps: deque[float] = deque()

    @property
    def policy(self) -> RateLimitPolicy:
        return self._policy

    def _evict_old(self, now: float) -> None:
        cutoff = now - self._policy.window_seconds
        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()

    def current_count(self, now: float | None = None) -> int:
        self._evict_old(now if now is not None else time.monotonic())
        return len(self._timestamps)

    def check_and_record(self) -> None:
        now = time.monotonic()
        self._evict_old(now)
        if len(self._timestamps) >= self._policy.max_calls:
            raise RateLimitExceeded(self._policy.max_calls, self._policy.window_seconds)
        self._timestamps.append(now)

    def reset(self) -> None:
        self._timestamps.clear()
