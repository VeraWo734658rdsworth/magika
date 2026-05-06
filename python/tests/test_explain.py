"""Unit tests for magika.explain."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from magika.explain import (
    ExplanationFactor,
    PredictionExplanation,
    explain_result,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(label: str = "python", score: float = 0.95, group: str = "code"):
    output = MagicMock()
    output.ct_label = label
    output.score = score
    output.group = group
    result = MagicMock()
    result.output = output
    return result


# ---------------------------------------------------------------------------
# ExplanationFactor
# ---------------------------------------------------------------------------

class TestExplanationFactor:
    def test_str_contains_name(self):
        f = ExplanationFactor(name="model_score", description="NN score", weight=0.9)
        assert "model_score" in str(f)

    def test_str_contains_percentage(self):
        f = ExplanationFactor(name="x", description="d", weight=0.75)
        assert "75%" in str(f)

    def test_weight_clamped_in_explain(self):
        result = _make_result(score=1.5)  # over 1.0 on purpose
        exp = explain_result(result)
        for factor in exp.factors:
            assert factor.weight <= 1.0


# ---------------------------------------------------------------------------
# explain_result
# ---------------------------------------------------------------------------

class TestExplainResult:
    def test_returns_prediction_explanation(self):
        result = _make_result()
        exp = explain_result(result)
        assert isinstance(exp, PredictionExplanation)

    def test_factors_not_empty(self):
        exp = explain_result(_make_result())
        assert len(exp.factors) > 0

    def test_summary_contains_label(self):
        exp = explain_result(_make_result(label="pdf"))
        assert "pdf" in exp.summary

    def test_summary_high_confidence(self):
        exp = explain_result(_make_result(score=0.99))
        assert "high" in exp.summary

    def test_summary_medium_confidence(self):
        exp = explain_result(_make_result(score=0.70))
        assert "medium" in exp.summary

    def test_summary_low_confidence(self):
        exp = explain_result(_make_result(score=0.30))
        assert "low" in exp.summary

    def test_model_score_factor_present(self):
        exp = explain_result(_make_result())
        names = [f.name for f in exp.factors]
        assert "model_score" in names

    def test_content_group_factor_present(self):
        exp = explain_result(_make_result(group="text"))
        names = [f.name for f in exp.factors]
        assert "content_group" in names

    def test_str_contains_score(self):
        exp = explain_result(_make_result(score=0.88))
        assert "0.8800" in str(exp)
