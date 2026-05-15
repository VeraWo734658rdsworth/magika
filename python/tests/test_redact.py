"""Tests for magika.redact."""

from __future__ import annotations

import pytest

from magika.redact import RedactionEngine, RedactionError, RedactionRule


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(label: str = "python", score: float = 0.99):
    """Return a minimal MagikaResult-like object sufficient for redaction tests."""
    from unittest.mock import MagicMock

    result = MagicMock()
    result.prediction.dl.ct_label = label
    result.prediction.score = score
    return result


# ---------------------------------------------------------------------------
# RedactionRule construction
# ---------------------------------------------------------------------------

class TestRedactionRule:
    def test_empty_replacement_raises(self):
        with pytest.raises(RedactionError, match="replacement"):
            RedactionRule(replacement="", labels={"python"})

    def test_whitespace_replacement_raises(self):
        with pytest.raises(RedactionError, match="replacement"):
            RedactionRule(replacement="   ", labels={"python"})

    def test_no_labels_and_no_predicate_raises(self):
        with pytest.raises(RedactionError, match="at least one"):
            RedactionRule(replacement="redacted")

    def test_labels_stored_as_frozenset(self):
        rule = RedactionRule(replacement="redacted", labels={"python", "javascript"})
        assert isinstance(rule.labels, frozenset)
        assert "python" in rule.labels

    def test_matches_by_label(self):
        rule = RedactionRule(replacement="redacted", labels={"python"})
        result = _make_result(label="python")
        assert rule.matches(result) is True

    def test_no_match_different_label(self):
        rule = RedactionRule(replacement="redacted", labels={"javascript"})
        result = _make_result(label="python")
        assert rule.matches(result) is False

    def test_matches_by_predicate(self):
        rule = RedactionRule(
            replacement="low-confidence",
            predicate=lambda r: r.prediction.score < 0.5,
        )
        result = _make_result(score=0.3)
        assert rule.matches(result) is True

    def test_predicate_overrides_label_check(self):
        rule = RedactionRule(
            replacement="flagged",
            predicate=lambda r: True,
        )
        result = _make_result(label="pdf")
        assert rule.matches(result) is True


# ---------------------------------------------------------------------------
# RedactionEngine
# ---------------------------------------------------------------------------

class TestRedactionEngine:
    def test_add_non_rule_raises(self):
        engine = RedactionEngine()
        with pytest.raises(RedactionError):
            engine.add_rule("not-a-rule")  # type: ignore[arg-type]

    def test_no_rules_returns_original(self):
        engine = RedactionEngine()
        result = _make_result(label="python")
        out = engine.redact(result)
        assert out.prediction.dl.ct_label == "python"

    def test_matching_rule_relabels(self):
        engine = RedactionEngine()
        engine.add_rule(RedactionRule(replacement="redacted", labels={"python"}))
        result = _make_result(label="python")
        out = engine.redact(result)
        assert out.prediction.dl.ct_label == "redacted"

    def test_first_matching_rule_wins(self):
        engine = RedactionEngine()
        engine.add_rule(RedactionRule(replacement="first", labels={"python"}))
        engine.add_rule(RedactionRule(replacement="second", labels={"python"}))
        result = _make_result(label="python")
        out = engine.redact(result)
        assert out.prediction.dl.ct_label == "first"

    def test_redact_many(self):
        engine = RedactionEngine()
        engine.add_rule(RedactionRule(replacement="safe", labels={"python"}))
        results = [_make_result(label="python"), _make_result(label="pdf")]
        out = engine.redact_many(results)
        assert out[0].prediction.dl.ct_label == "safe"
        assert out[1].prediction.dl.ct_label == "pdf"

    def test_original_result_not_mutated(self):
        engine = RedactionEngine()
        engine.add_rule(RedactionRule(replacement="redacted", labels={"python"}))
        result = _make_result(label="python")
        engine.redact(result)
        assert result.prediction.dl.ct_label == "python"
