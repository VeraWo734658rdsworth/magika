"""Quarantine support: flag results whose labels match a quarantine list."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Set

from magika.prediction import MagikaResult


class QuarantineError(ValueError):
    """Raised when the quarantine configuration is invalid."""


@dataclass
class QuarantinePolicy:
    """Defines which labels should be quarantined."""

    labels: Set[str] = field(default_factory=set)
    mime_types: Set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if not self.labels and not self.mime_types:
            raise QuarantineError(
                "QuarantinePolicy requires at least one label or mime type."
            )
        self.labels = {lbl.lower().strip() for lbl in self.labels}
        self.mime_types = {m.lower().strip() for m in self.mime_types}

    @classmethod
    def from_labels(cls, labels: Iterable[str]) -> "QuarantinePolicy":
        return cls(labels=set(labels))

    @classmethod
    def from_mime_types(cls, mime_types: Iterable[str]) -> "QuarantinePolicy":
        return cls(mime_types=set(mime_types))

    def should_quarantine(self, result: MagikaResult) -> bool:
        label = (result.prediction.label or "").lower().strip()
        mime = (result.prediction.mime_type or "").lower().strip()
        return label in self.labels or mime in self.mime_types


@dataclass
class QuarantineEntry:
    result: MagikaResult
    reason: str

    def to_dict(self) -> dict:
        return {
            "label": self.result.prediction.label,
            "mime_type": self.result.prediction.mime_type,
            "score": round(self.result.prediction.score, 4),
            "reason": self.reason,
        }

    def __repr__(self) -> str:
        return (
            f"QuarantineEntry(label={self.result.prediction.label!r}, "
            f"reason={self.reason!r})"
        )


def apply_quarantine(
    results: List[MagikaResult],
    policy: QuarantinePolicy,
) -> tuple[List[MagikaResult], List[QuarantineEntry]]:
    """Split results into clean and quarantined lists."""
    clean: List[MagikaResult] = []
    quarantined: List[QuarantineEntry] = []
    for result in results:
        if policy.should_quarantine(result):
            label = result.prediction.label or ""
            mime = result.prediction.mime_type or ""
            reason = (
                f"label '{label}' matched quarantine policy"
                if label.lower() in policy.labels
                else f"mime '{mime}' matched quarantine policy"
            )
            quarantined.append(QuarantineEntry(result=result, reason=reason))
        else:
            clean.append(result)
    return clean, quarantined
