"""Integration-style tests for the explain feature (no real model needed)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from magika.explain import ExplanationFactor, PredictionExplanation, explain_result
from magika.explain_magika import ExplainMagika


def _result(label, score, group="text"):
    out = MagicMock(ct_label=label, score=score, group=group)
    r = MagicMock()
    r.output = out
    return r


# ---------------------------------------------------------------------------
# Factor weight invariants
# ---------------------------------------------------------------------------

def test_all_factor_weights_in_range():
    for score in (0.1, 0.5, 0.9, 1.0):
        exp = explain_result(_result("txt", score))
        for f in exp.factors:
            assert 0.0 <= f.weight <= 1.0, f"weight out of range: {f}"


def test_explanation_str_round_trip():
    exp = explain_result(_result("pdf", 0.87, "document"))
    s = str(exp)
    assert "pdf" in s
    assert "document" in s
    assert "0.8700" in s


# ---------------------------------------------------------------------------
# Pipeline: ExplainMagika preserves result identity
# ---------------------------------------------------------------------------

def test_result_identity_preserved():
    r = _result("python", 0.99, "code")
    magika_mock = MagicMock()
    magika_mock.identify_bytes.return_value = r
    em = ExplainMagika(magika=magika_mock)
    result, exp = em.identify_bytes(b"x = 1")
    assert result is r
    assert exp.result is r


# ---------------------------------------------------------------------------
# Multiple results via identify_paths
# ---------------------------------------------------------------------------

def test_identify_paths_explanations_match_results():
    results = [_result("python", 0.95), _result("pdf", 0.80)]
    magika_mock = MagicMock()
    magika_mock.identify_paths.return_value = results
    em = ExplainMagika(magika=magika_mock)
    pairs = em.identify_paths([MagicMock(), MagicMock()])
    for (res, exp), expected_result in zip(pairs, results):
        assert res is expected_result
        assert exp.result is expected_result


# ---------------------------------------------------------------------------
# Summary language
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("score,expected_word", [
    (0.95, "high"),
    (0.65, "medium"),
    (0.20, "low"),
])
def test_summary_confidence_word(score, expected_word):
    exp = explain_result(_result("txt", score))
    assert expected_word in exp.summary
