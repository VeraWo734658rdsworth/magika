"""MagikaLike wrapper that quarantines results matching a QuarantinePolicy."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Sequence

from magika.pipeline import MagikaLike
from magika.prediction import MagikaResult
from magika.quarantine import QuarantineEntry, QuarantinePolicy, apply_quarantine


class QuarantineMagika:
    """Wraps a MagikaLike and separates quarantined results from clean ones."""

    def __init__(self, inner: MagikaLike, policy: QuarantinePolicy) -> None:
        self._inner = inner
        self._policy = policy
        self._quarantined: List[QuarantineEntry] = []

    @property
    def quarantined(self) -> List[QuarantineEntry]:
        """All quarantined entries collected so far."""
        return list(self._quarantined)

    def clear_quarantine(self) -> None:
        """Reset the quarantine log."""
        self._quarantined.clear()

    def identify_bytes(self, content: bytes) -> MagikaResult:
        result = self._inner.identify_bytes(content)
        clean, flagged = apply_quarantine([result], self._policy)
        self._quarantined.extend(flagged)
        return clean[0] if clean else result

    def identify_path(self, path: Path) -> MagikaResult:
        result = self._inner.identify_path(path)
        clean, flagged = apply_quarantine([result], self._policy)
        self._quarantined.extend(flagged)
        return clean[0] if clean else result

    def identify_paths(self, paths: Sequence[Path]) -> List[MagikaResult]:
        results = self._inner.identify_paths(paths)
        clean, flagged = apply_quarantine(list(results), self._policy)
        self._quarantined.extend(flagged)
        return clean
