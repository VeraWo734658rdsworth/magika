"""Retry logic for transient failures during file identification."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, TypeVar

T = TypeVar("T")


class RetryExhausted(Exception):
    """Raised when all retry attempts have been exhausted."""

    def __init__(self, attempts: int, last_error: Exception) -> None:
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(f"Failed after {attempts} attempt(s): {last_error}")


@dataclass
class RetryPolicy:
    """Configuration for retry behaviour."""

    max_attempts: int = 3
    delay_seconds: float = 0.1
    backoff_factor: float = 2.0
    exceptions: tuple[type[Exception], ...] = field(
        default_factory=lambda: (OSError, IOError)
    )

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.delay_seconds < 0:
            raise ValueError("delay_seconds must be >= 0")
        if self.backoff_factor < 1.0:
            raise ValueError("backoff_factor must be >= 1.0")


def with_retry(fn: Callable[[], T], policy: RetryPolicy) -> T:
    """Execute *fn* according to *policy*, retrying on transient errors.

    Returns the result of *fn* on success.  Raises :class:`RetryExhausted`
    when every attempt fails.
    """
    delay = policy.delay_seconds
    last_exc: Exception | None = None

    for attempt in range(1, policy.max_attempts + 1):
        try:
            return fn()
        except policy.exceptions as exc:  # type: ignore[misc]
            last_exc = exc
            if attempt < policy.max_attempts:
                time.sleep(delay)
                delay *= policy.backoff_factor

    raise RetryExhausted(policy.max_attempts, last_exc)  # type: ignore[arg-type]
