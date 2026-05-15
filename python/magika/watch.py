"""File-system watch helper: poll a directory and yield new paths."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator, List, Optional, Set


class WatchError(Exception):
    """Raised when the watch configuration is invalid."""


@dataclass
class WatchPolicy:
    """Configuration for a directory-watch session."""

    interval_seconds: float = 2.0
    recursive: bool = False
    extensions: Optional[List[str]] = None  # None means all extensions

    def __post_init__(self) -> None:
        if self.interval_seconds <= 0:
            raise WatchError("interval_seconds must be positive")
        if self.extensions is not None:
            normalised = []
            for ext in self.extensions:
                ext = ext.strip()
                if not ext:
                    raise WatchError("extension must not be empty")
                normalised.append(ext.lower().lstrip("."))
            self.extensions = normalised

    def matches(self, path: Path) -> bool:
        """Return True if *path* passes the extension filter."""
        if self.extensions is None:
            return True
        return path.suffix.lower().lstrip(".") in self.extensions


@dataclass
class WatchSession:
    """Tracks which paths have already been seen."""

    _seen: Set[Path] = field(default_factory=set)

    def snapshot(self, directory: Path, policy: WatchPolicy) -> List[Path]:
        """Return paths that are new since the last snapshot."""
        pattern = "**/*" if policy.recursive else "*"
        current: Set[Path] = {
            p for p in directory.glob(pattern)
            if p.is_file() and policy.matches(p)
        }
        new_paths = sorted(current - self._seen)
        self._seen.update(current)
        return new_paths

    @property
    def seen_count(self) -> int:
        return len(self._seen)


def watch(
    directory: Path,
    policy: WatchPolicy,
    callback: Callable[[List[Path]], None],
    *,
    max_iterations: Optional[int] = None,
    _sleep: Callable[[float], None] = time.sleep,
) -> None:
    """Poll *directory* and invoke *callback* with each batch of new paths."""
    if not directory.is_dir():
        raise WatchError(f"Not a directory: {directory}")

    session = WatchSession()
    iterations = 0
    while max_iterations is None or iterations < max_iterations:
        new_paths = session.snapshot(directory, policy)
        if new_paths:
            callback(new_paths)
        _sleep(policy.interval_seconds)
        iterations += 1
