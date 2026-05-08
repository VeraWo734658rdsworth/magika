"""Magika wrapper that enforces a sliding-window request quota."""
from __future__ import annotations

from pathlib import Path
from typing import List

from magika.magika import Magika
from magika.prediction import MagikaResult
from magika.quota import QuotaPolicy, QuotaTracker


class QuotaMagika:
    """Wraps a Magika instance and enforces per-call quota limits.

    Each call to identify_path / identify_paths / identify_bytes counts as
    *one* request regardless of how many files are in the batch.
    """

    def __init__(
        self,
        inner: Magika,
        policy: QuotaPolicy | None = None,
    ) -> None:
        self._inner = inner
        self._tracker = QuotaTracker(policy=policy or QuotaPolicy())

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @property
    def tracker(self) -> QuotaTracker:
        return self._tracker

    def reset_quota(self) -> None:
        """Reset the quota window (e.g. for testing)."""
        self._tracker.reset()

    # ------------------------------------------------------------------
    # Identification API
    # ------------------------------------------------------------------

    def identify_bytes(self, data: bytes) -> MagikaResult:
        self._tracker.check_and_record()
        return self._inner.identify_bytes(data)

    def identify_path(self, path: Path) -> MagikaResult:
        self._tracker.check_and_record()
        return self._inner.identify_path(path)

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        self._tracker.check_and_record()
        return self._inner.identify_paths(paths)
