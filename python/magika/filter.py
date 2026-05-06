"""Filter utilities for restricting Magika results by MIME type, group, or label."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from magika.prediction import MagikaResult


@dataclass
class ResultFilter:
    """Declarative filter applied to a sequence of MagikaResults."""

    labels: List[str] = field(default_factory=list)
    mime_types: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)
    min_score: float = 0.0

    def matches(self, result: MagikaResult) -> bool:
        """Return True if *result* passes every active criterion."""
        info = result.prediction.content_type_info

        if self.labels and info.label not in self.labels:
            return False

        if self.mime_types and info.mime_type not in self.mime_types:
            return False

        if self.groups and info.group not in self.groups:
            return False

        if result.prediction.score < self.min_score:
            return False

        return True

    def apply(self, results: Iterable[MagikaResult]) -> List[MagikaResult]:
        """Return the subset of *results* that satisfy this filter."""
        return [r for r in results if self.matches(r)]


def filter_by_label(
    results: Iterable[MagikaResult], labels: Iterable[str]
) -> List[MagikaResult]:
    """Convenience wrapper: keep only results whose label is in *labels*."""
    return ResultFilter(labels=list(labels)).apply(results)


def filter_by_group(
    results: Iterable[MagikaResult], groups: Iterable[str]
) -> List[MagikaResult]:
    """Convenience wrapper: keep only results whose group is in *groups*."""
    return ResultFilter(groups=list(groups)).apply(results)


def filter_by_min_score(
    results: Iterable[MagikaResult], min_score: float
) -> List[MagikaResult]:
    """Convenience wrapper: keep only results with score >= *min_score*."""
    return ResultFilter(min_score=min_score).apply(results)
