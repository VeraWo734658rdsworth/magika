"""Tests for python/magika/scorer.py."""

from __future__ import annotations

import pytest

from magika.scorer import (
    DEFAULT_THRESHOLD,
    UNKNOWN_LABEL,
    ScoredPrediction,
    apply_threshold,
    top_k_predictions,
    top_prediction,
)


# ---------------------------------------------------------------------------
# ScoredPrediction
# ---------------------------------------------------------------------------

class TestScoredPrediction:
    def test_is_confident_above_threshold(self):
        sp = ScoredPrediction(label="pdf", score=0.9)
        assert sp.is_confident() is True

    def test_is_confident_at_threshold(self):
        sp = ScoredPrediction(label="pdf", score=DEFAULT_THRESHOLD)
        assert sp.is_confident() is True

    def test_is_confident_below_threshold(self):
        sp = ScoredPrediction(label="pdf", score=0.1)
        assert sp.is_confident() is False

    def test_is_confident_custom_threshold(self):
        sp = ScoredPrediction(label="pdf", score=0.7)
        assert sp.is_confident(threshold=0.8) is False
        assert sp.is_confident(threshold=0.7) is True


# ---------------------------------------------------------------------------
# top_prediction
# ---------------------------------------------------------------------------

class TestTopPrediction:
    def test_single_entry(self):
        result = top_prediction({"pdf": 0.99})
        assert result.label == "pdf"
        assert result.score == pytest.approx(0.99)

    def test_multiple_entries_returns_highest(self):
        scores = {"pdf": 0.6, "zip": 0.9, "png": 0.3}
        result = top_prediction(scores)
        assert result.label == "zip"
        assert result.score == pytest.approx(0.9)

    def test_empty_scores_raises(self):
        with pytest.raises(ValueError, match="empty"):
            top_prediction({})


# ---------------------------------------------------------------------------
# apply_threshold
# ---------------------------------------------------------------------------

class TestApplyThreshold:
    def test_confident_prediction_unchanged(self):
        sp = ScoredPrediction(label="pdf", score=0.95)
        result = apply_threshold(sp)
        assert result.label == "pdf"
        assert result.score == pytest.approx(0.95)

    def test_low_confidence_returns_fallback_label(self):
        sp = ScoredPrediction(label="pdf", score=0.2)
        result = apply_threshold(sp)
        assert result.label == UNKNOWN_LABEL
        assert result.score == pytest.approx(0.2)

    def test_custom_fallback_label(self):
        sp = ScoredPrediction(label="pdf", score=0.1)
        result = apply_threshold(sp, fallback="generic")
        assert result.label == "generic"


# ---------------------------------------------------------------------------
# top_k_predictions
# ---------------------------------------------------------------------------

class TestTopKPredictions:
    def test_returns_k_items(self):
        scores = {"pdf": 0.8, "zip": 0.6, "png": 0.4, "txt": 0.2}
        result = top_k_predictions(scores, k=2)
        assert len(result) == 2

    def test_sorted_descending(self):
        scores = {"pdf": 0.3, "zip": 0.9, "png": 0.6}
        result = top_k_predictions(scores, k=3)
        assert [r.label for r in result] == ["zip", "png", "pdf"]

    def test_k_larger_than_scores_returns_all(self):
        scores = {"pdf": 0.8, "zip": 0.6}
        result = top_k_predictions(scores, k=10)
        assert len(result) == 2

    def test_k_zero_raises(self):
        with pytest.raises(ValueError, match="positive"):
            top_k_predictions({"pdf": 0.9}, k=0)
