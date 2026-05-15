"""Score clamping utilities for Magika predictions."""
from __future__ import annotations

from dataclasses import dataclass, field

from magika.prediction import MagikaResult


class ClampError(ValueError):
    """Raised when a ClampPolicy is misconfigured."""


@dataclass(frozen=True)
class ClampPolicy:
    """Defines the [low, high] range to which scores are clamped."""

    low: float = 0.0
    high: float = 1.0

    def __post_init__(self) -> None:
        if self.low < 0.0 or self.low > 1.0:
            raise ClampError(f"low must be in [0, 1], got {self.low}")
        if self.high < 0.0 or self.high > 1.0:
            raise ClampError(f"high must be in [0, 1], got {self.high}")
        if self.low > self.high:
            raise ClampError(
                f"low ({self.low}) must be <= high ({self.high})"
            )


def clamp_score(score: float, policy: ClampPolicy) -> float:
    """Return *score* clamped to the range defined by *policy*."""
    return max(policy.low, min(policy.high, score))


def clamp_result(result: MagikaResult, policy: ClampPolicy) -> MagikaResult:
    """Return a copy of *result* with its score clamped according to *policy*."""
    clamped = clamp_score(result.prediction.score, policy)
    if clamped == result.prediction.score:
        return result
    # Rebuild via the dataclass replace pattern (prediction is a dataclass).
    from dataclasses import replace

    new_prediction = replace(result.prediction, score=clamped)
    return replace(result, prediction=new_prediction)
