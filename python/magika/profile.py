"""Profiling utilities for Magika prediction timing."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ProfileEntry:
    path: Optional[Path]
    label: str
    elapsed_ms: float

    def to_dict(self) -> dict:
        return {
            "path": str(self.path) if self.path is not None else None,
            "label": self.label,
            "elapsed_ms": round(self.elapsed_ms, 3),
        }

    def __repr__(self) -> str:
        return (
            f"ProfileEntry(path={self.path!r}, label={self.label!r}, "
            f"elapsed_ms={self.elapsed_ms:.3f})"
        )


@dataclass
class ProfilingSession:
    entries: List[ProfileEntry] = field(default_factory=list)

    def record(self, path: Optional[Path], label: str, elapsed_ms: float) -> None:
        self.entries.append(ProfileEntry(path=path, label=label, elapsed_ms=elapsed_ms))

    def total_ms(self) -> float:
        return sum(e.elapsed_ms for e in self.entries)

    def average_ms(self) -> float:
        if not self.entries:
            return 0.0
        return self.total_ms() / len(self.entries)

    def slowest(self) -> Optional[ProfileEntry]:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.elapsed_ms)

    def clear(self) -> None:
        self.entries.clear()

    def __len__(self) -> int:
        return len(self.entries)


class Timer:
    """Context manager for measuring elapsed time in milliseconds."""

    def __init__(self) -> None:
        self._start: float = 0.0
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_) -> None:
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000.0
