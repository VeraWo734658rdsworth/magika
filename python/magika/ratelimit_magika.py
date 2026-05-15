"""Magika wrapper that enforces a sliding-window rate limit."""
from __future__ import annotations

from pathlib import Path
from typing import List

from magika.ratelimit import RateLimitPolicy, RateLimiter
from magika.prediction import MagikaResult


class RateLimitMagika:
    """Wraps a Magika-like object and raises RateLimitExceeded when the
    configured rate limit is breached."""

    def __init__(self, inner, policy: RateLimitPolicy | None = None) -> None:
        self._inner = inner
        self._limiter = RateLimiter(policy or RateLimitPolicy())

    @property
    def limiter(self) -> RateLimiter:
        return self._limiter

    def reset_limit(self) -> None:
        """Reset the sliding window (useful between test scenarios)."""
        self._limiter.reset()

    def identify_bytes(self, data: bytes) -> MagikaResult:
        self._limiter.check_and_record()
        return self._inner.identify_bytes(data)

    def identify_path(self, path: Path) -> MagikaResult:
        self._limiter.check_and_record()
        return self._inner.identify_path(path)

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        for _ in paths:
            self._limiter.check_and_record()
        return self._inner.identify_paths(paths)
