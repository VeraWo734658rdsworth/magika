"""Rate/quota limiting for Magika inference calls."""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque


class QuotaExceeded(Exception):
    """Raised when the request quota has been exhausted."""

    def __init__(self, limit: int, window: float) -> None:
        super().__init__(
            f"Quota of {limit} requests per {window:.1f}s window exceeded"
        )
        self.limit = limit
        self.window = window


@dataclass
class QuotaPolicy:
    """Sliding-window quota policy."""

    max_requests: int = 1000
    window_seconds: float = 60.0

    def __post_init__(self) -> None:
        if self.max_requests < 1:
            raise ValueError("max_requests must be >= 1")
        if self.window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")


@dataclass
class QuotaTracker:
    """Tracks request timestamps within a sliding window."""

    policy: QuotaPolicy = field(default_factory=QuotaPolicy)
    _timestamps: Deque[float] = field(default_factory=deque, init=False, repr=False)

    def _evict_old(self, now: float) -> None:
        cutoff = now - self.policy.window_seconds
        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()

    def check_and_record(self) -> None:
        """Record a request or raise QuotaExceeded."""
        now = time.monotonic()
        self._evict_old(now)
        if len(self._timestamps) >= self.policy.max_requests:
            raise QuotaExceeded(self.policy.max_requests, self.policy.window_seconds)
        self._timestamps.append(now)

    @property
    def current_count(self) -> int:
        """Number of requests in the current window."""
        self._evict_old(time.monotonic())
        return len(self._timestamps)

    def reset(self) -> None:
        """Clear all recorded timestamps."""
        self._timestamps.clear()
