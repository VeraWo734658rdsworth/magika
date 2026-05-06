"""Utilities for scoring and thresholding model predictions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# Default confidence threshold below which a prediction is considered low-confidence.
DEFAULT_THRESHOLD: float = 0.5

# Label used when no prediction clears the confidence threshold.
UNKNOWN_LABEL: str = "unknown"


@dataclass(frozen=True)
class ScoredPrediction:
    """A label paired with its confidence score."""

    label: str
    score: float

    def is_confident(self, threshold: float = DEFAULT_THRESHOLD) -> bool:
        """Return True when the score meets or exceeds *threshold*."""
        return self.score >= threshold

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.label} ({self.score:.4f})"


def top_prediction(scores: Dict[str, float]) -> ScoredPrediction:
    """Return the label with the highest score from a scores mapping.

    Args:
        scores: Mapping of label -> confidence score (0.0 – 1.0).

    Returns:
        A :class:`ScoredPrediction` for the best-scoring label.

    Raises:
        ValueError: If *scores* is empty.
    """
    if not scores:
        raise ValueError("scores mapping must not be empty")
    label = max(scores, key=lambda k: scores[k])
    return ScoredPrediction(label=label, score=scores[label])


def apply_threshold(
    prediction: ScoredPrediction,
    threshold: float = DEFAULT_THRESHOLD,
    fallback: str = UNKNOWN_LABEL,
) -> ScoredPrediction:
    """Return *prediction* unchanged if confident, otherwise return a fallback.

    Args:
        prediction: The scored prediction to evaluate.
        threshold:  Minimum score required to keep the prediction.
        fallback:   Label to use when the score is below *threshold*.

    Returns:
        Either the original prediction or a new one with *fallback* label and
        the original score preserved for traceability.
    """
    if prediction.is_confident(threshold):
        return prediction
    return ScoredPrediction(label=fallback, score=prediction.score)


def top_k_predictions(
    scores: Dict[str, float], k: int = 3
) -> List[ScoredPrediction]:
    """Return the top-*k* predictions sorted by descending score.

    Args:
        scores: Mapping of label -> confidence score.
        k:      Number of predictions to return.

    Returns:
        List of :class:`ScoredPrediction` objects, highest score first.
    """
    if k <= 0:
        raise ValueError("k must be a positive integer")
    sorted_items: List[Tuple[str, float]] = sorted(
        scores.items(), key=lambda item: item[1], reverse=True
    )
    return [ScoredPrediction(label=lbl, score=sc) for lbl, sc in sorted_items[:k]]
