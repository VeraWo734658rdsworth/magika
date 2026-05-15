"""Magika wrapper that accumulates a structured Report alongside predictions."""
from __future__ import annotations

from pathlib import Path
from typing import List

from magika.pipeline import MagikaLike
from magika.prediction import MagikaResult
from magika.report import Report


class ReportMagika:
    """Wraps a MagikaLike and builds a Report from every prediction made."""

    def __init__(self, inner: MagikaLike) -> None:
        if not isinstance(inner, MagikaLike):
            raise TypeError("inner must implement MagikaLike")
        self._inner = inner
        self._report = Report()

    @property
    def report(self) -> Report:
        return self._report

    def clear_report(self) -> None:
        self._report = Report()

    def identify_bytes(self, content: bytes) -> MagikaResult:
        result = self._inner.identify_bytes(content)
        self._report.add(result)
        return result

    def identify_path(self, path: Path) -> MagikaResult:
        result = self._inner.identify_path(path)
        self._report.add(result, path)
        return result

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        results = self._inner.identify_paths(paths)
        self._report.add_many(results, paths)
        return results
