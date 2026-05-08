"""Magika wrapper that enforces a wall-clock timeout on every identification call."""

from __future__ import annotations

from pathlib import Path
from typing import List

from magika.magika import Magika
from magika.prediction import MagikaResult
from magika.timeout import TimeoutPolicy, _run_with_timeout


class TimeoutMagika:
    """Wraps a :class:`Magika` instance and enforces a per-call timeout.

    Parameters
    ----------
    inner:
        Underlying :class:`Magika` (or compatible) instance.
    policy:
        :class:`TimeoutPolicy` controlling how long each call may run.
    """

    def __init__(self, inner: Magika, policy: TimeoutPolicy | None = None) -> None:
        self._inner = inner
        self._policy = policy or TimeoutPolicy()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def identify_bytes(self, data: bytes) -> MagikaResult:
        """Identify *data*, raising :class:`TimeoutExceeded` if too slow."""
        return _run_with_timeout(lambda: self._inner.identify_bytes(data), self._policy)

    def identify_path(self, path: Path) -> MagikaResult:
        """Identify the file at *path*, raising :class:`TimeoutExceeded` if too slow."""
        return _run_with_timeout(lambda: self._inner.identify_path(path), self._policy)

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        """Identify all *paths*, raising :class:`TimeoutExceeded` if too slow."""
        return _run_with_timeout(
            lambda: self._inner.identify_paths(paths), self._policy
        )
