"""Statistics tracking for Magika predictions."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

from magika.prediction import MagikaResult


@dataclass
class PredictionStats:
    """Aggregated statistics over a set of Magika predictions."""

    total: int = 0
    label_counts: Dict[str, int] = field(default_factory=Counter)
    group_counts: Dict[str, int] = field(default_factory=Counter)
    score_sum: float = 0.0
    low_confidence_count: int = 0
    low_confidence_threshold: float = 0.7

    def update(self, result: MagikaResult) -> None:
        """Update statistics with a single prediction result."""
        self.total += 1
        label = result.output.ct_label
        group = result.output.group
        score = result.output.score

        self.label_counts[label] = self.label_counts.get(label, 0) + 1
        self.group_counts[group] = self.group_counts.get(group, 0) + 1
        self.score_sum += score

        if score < self.low_confidence_threshold:
            self.low_confidence_count += 1

    def update_many(self, results: List[MagikaResult]) -> None:
        """Update statistics with multiple prediction results."""
        for result in results:
            self.update(result)

    @property
    def average_score(self) -> float:
        """Return the average confidence score across all predictions."""
        if self.total == 0:
            return 0.0
        return self.score_sum / self.total

    @property
    def most_common_label(self) -> str | None:
        """Return the most frequently predicted label."""
        if not self.label_counts:
            return None
        return max(self.label_counts, key=lambda k: self.label_counts[k])

    @property
    def most_common_group(self) -> str | None:
        """Return the most frequently predicted group."""
        if not self.group_counts:
            return None
        return max(self.group_counts, key=lambda k: self.group_counts[k])

    def to_dict(self) -> dict:
        """Serialize statistics to a plain dictionary."""
        return {
            "total": self.total,
            "average_score": round(self.average_score, 4),
            "low_confidence_count": self.low_confidence_count,
            "low_confidence_threshold": self.low_confidence_threshold,
            "most_common_label": self.most_common_label,
            "most_common_group": self.most_common_group,
            "label_counts": dict(self.label_counts),
            "group_counts": dict(self.group_counts),
        }

    def __repr__(self) -> str:
        return (
            f"PredictionStats(total={self.total}, "
            f"avg_score={self.average_score:.3f}, "
            f"low_confidence={self.low_confidence_count})"
        )
