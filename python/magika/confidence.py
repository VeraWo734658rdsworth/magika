"""Confidence tier classification for Magika predictions."""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass


class ConfidenceTier(str, Enum):
    """Broad confidence band for a model prediction score."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

    def __str__(self) -> str:  # pragma: no cover
        return self.value


# Default thresholds (inclusive lower bound for each tier).
_DEFAULT_HIGH: float = 0.90
_DEFAULT_MEDIUM: float = 0.70


@dataclass(frozen=True)
class ConfidenceThresholds:
    """Configurable thresholds that separate confidence tiers."""

    high: float = _DEFAULT_HIGH
    medium: float = _DEFAULT_MEDIUM

    def __post_init__(self) -> None:
        if not (0.0 <= self.medium <= self.high <= 1.0):
            raise ValueError(
                f"Thresholds must satisfy 0 ≤ medium ({self.medium}) "
                f"≤ high ({self.high}) ≤ 1"
            )


_DEFAULT_THRESHOLDS = ConfidenceThresholds()


def classify_score(
    score: float,
    thresholds: ConfidenceThresholds = _DEFAULT_THRESHOLDS,
) -> ConfidenceTier:
    """Return the :class:`ConfidenceTier` for *score*.

    Args:
        score: A probability-like value in ``[0, 1]``.
        thresholds: Tier boundaries to use (defaults to 0.90 / 0.70).

    Returns:
        The matching :class:`ConfidenceTier`.

    Raises:
        ValueError: If *score* is outside ``[0, 1]``.
    """
    if not (0.0 <= score <= 1.0):
        raise ValueError(f"score must be in [0, 1], got {score!r}")

    if score >= thresholds.high:
        return ConfidenceTier.HIGH
    if score >= thresholds.medium:
        return ConfidenceTier.MEDIUM
    if score > 0.0:
        return ConfidenceTier.LOW
    return ConfidenceTier.UNKNOWN


def tier_label(score: float) -> str:
    """Convenience wrapper that returns the tier value as a plain string."""
    return classify_score(score).value
