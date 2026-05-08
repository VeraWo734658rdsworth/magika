"""Timeout policy and enforcement for Magika identification calls."""

from __future__ import annotations

import signal
import threading
from dataclasses import dataclass, field
from typing import Callable, TypeVar

F = TypeVar("F")


class TimeoutExceeded(Exception):
    """Raised when an identification call exceeds the allowed wall-clock time."""

    def __init__(self, seconds: float) -> None:
        super().__init__(f"Identification timed out after {seconds}s")
        self.seconds = seconds


@dataclass
class TimeoutPolicy:
    """Configuration for timeout enforcement."""

    seconds: float = 30.0
    """Maximum seconds allowed per call. Must be positive."""

    def __post_init__(self) -> None:
        if self.seconds <= 0:
            raise ValueError(f"seconds must be positive, got {self.seconds}")


def _run_with_timeout(fn: Callable[[], F], policy: TimeoutPolicy) -> F:
    """Run *fn* and raise TimeoutExceeded if it takes longer than policy.seconds.

    Uses a background thread so it works on all platforms (no SIGALRM on Windows).
    """
    result: list[F] = []
    exc: list[BaseException] = []

    def _target() -> None:
        try:
            result.append(fn())
        except BaseException as e:  # noqa: BLE001
            exc.append(e)

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join(timeout=policy.seconds)

    if t.is_alive():
        raise TimeoutExceeded(policy.seconds)

    if exc:
        raise exc[0]

    return result[0]
