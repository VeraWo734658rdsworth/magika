"""Tests for python/magika/confidence.py."""

from __future__ import annotations

import pytest

from magika.confidence import (
    ConfidenceTier,
    ConfidenceThresholds,
    classify_score,
    tier_label,
)


# ---------------------------------------------------------------------------
# ConfidenceThresholds validation
# ---------------------------------------------------------------------------


def test_default_thresholds_are_valid() -> None:
    t = ConfidenceThresholds()
    assert t.high == 0.90
    assert t.medium == 0.70


def test_custom_thresholds_accepted() -> None:
    t = ConfidenceThresholds(high=0.80, medium=0.50)
    assert t.high == 0.80
    assert t.medium == 0.50


def test_thresholds_reject_medium_above_high() -> None:
    with pytest.raises(ValueError, match="medium"):
        ConfidenceThresholds(high=0.60, medium=0.80)


def test_thresholds_reject_negative_values() -> None:
    with pytest.raises(ValueError):
        ConfidenceThresholds(high=-0.1, medium=-0.5)


# ---------------------------------------------------------------------------
# classify_score — boundary & interior values
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "score, expected",
    [
        (1.0, ConfidenceTier.HIGH),
        (0.95, ConfidenceTier.HIGH),
        (0.90, ConfidenceTier.HIGH),   # inclusive lower bound
        (0.89, ConfidenceTier.MEDIUM),
        (0.70, ConfidenceTier.MEDIUM),  # inclusive lower bound
        (0.69, ConfidenceTier.LOW),
        (0.01, ConfidenceTier.LOW),
        (0.0, ConfidenceTier.UNKNOWN),
    ],
)
def test_classify_score_default_thresholds(
    score: float, expected: ConfidenceTier
) -> None:
    assert classify_score(score) == expected


def test_classify_score_custom_thresholds() -> None:
    t = ConfidenceThresholds(high=0.80, medium=0.50)
    assert classify_score(0.85, t) == ConfidenceTier.HIGH
    assert classify_score(0.79, t) == ConfidenceTier.MEDIUM
    assert classify_score(0.49, t) == ConfidenceTier.LOW
    assert classify_score(0.0, t) == ConfidenceTier.UNKNOWN


def test_classify_score_rejects_out_of_range() -> None:
    with pytest.raises(ValueError, match="score must be in"):
        classify_score(1.1)
    with pytest.raises(ValueError):
        classify_score(-0.01)


# ---------------------------------------------------------------------------
# tier_label convenience wrapper
# ---------------------------------------------------------------------------


def test_tier_label_returns_string() -> None:
    assert tier_label(0.95) == "high"
    assert tier_label(0.75) == "medium"
    assert tier_label(0.30) == "low"
    assert tier_label(0.0) == "unknown"


# ---------------------------------------------------------------------------
# ConfidenceTier str representation
# ---------------------------------------------------------------------------


def test_confidence_tier_str() -> None:
    assert str(ConfidenceTier.HIGH) == "high"
    assert str(ConfidenceTier.UNKNOWN) == "unknown"
