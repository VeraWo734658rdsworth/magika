"""Byte-budget-aware wrapper around any MagikaLike engine."""
from __future__ import annotations

from pathlib import Path
from typing import List

from magika.budget import BudgetPolicy, BudgetTracker
from magika.pipeline import MagikaLike
from magika.prediction import MagikaResult


class BudgetMagika:
    """Wraps an inner engine and enforces a cumulative byte budget.

    Each call to *identify_bytes* counts the length of the supplied buffer
    against the budget.  Path-based calls stat the file first so the budget
    is checked before any inference is attempted.
    """

    def __init__(self, inner: MagikaLike, policy: BudgetPolicy) -> None:
        self._inner = inner
        self._tracker = BudgetTracker(policy=policy)

    @property
    def tracker(self) -> BudgetTracker:
        return self._tracker

    def reset_budget(self) -> None:
        """Reset the consumed-bytes counter to zero."""
        self._tracker.reset()

    def identify_bytes(self, data: bytes) -> MagikaResult:
        self._tracker.consume(len(data))
        return self._inner.identify_bytes(data)

    def identify_path(self, path: Path) -> MagikaResult:
        size = path.stat().st_size
        self._tracker.consume(size)
        return self._inner.identify_path(path)

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        results: List[MagikaResult] = []
        for p in paths:
            results.append(self.identify_path(p))
        return results
