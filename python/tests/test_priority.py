"""Tests for priority.py and priority_magika.py."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.priority import PriorityEngine, PriorityRule
from magika.priority_magika import PriorityMagika


def _mock_result(label: str, score: float = 0.9) -> MagicMock:
    r = MagicMock()
    r.prediction.label = label
    r.prediction.score = score
    return r


# --- PriorityRule ---

class TestPriorityRule:
    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            PriorityRule(name="", predicate=lambda r: True)

    def test_whitespace_name_raises(self):
        with pytest.raises(ValueError):
            PriorityRule(name="   ", predicate=lambda r: True)

    def test_matches_returns_predicate_result(self):
        rule = PriorityRule(name="pdf", predicate=lambda r: r.prediction.label == "pdf")
        assert rule.matches(_mock_result("pdf")) is True
        assert rule.matches(_mock_result("txt")) is False

    def test_repr_contains_name_and_priority(self):
        rule = PriorityRule(name="img", predicate=lambda r: True, priority=5)
        assert "img" in repr(rule)
        assert "5" in repr(rule)


# --- PriorityEngine ---

class TestPriorityEngine:
    def test_select_empty_returns_none(self):
        engine = PriorityEngine()
        assert engine.select([]) is None

    def test_select_no_rules_returns_first(self):
        engine = PriorityEngine()
        r1 = _mock_result("pdf")
        r2 = _mock_result("txt")
        assert engine.select([r1, r2]) is r1

    def test_select_picks_highest_priority_match(self):
        engine = PriorityEngine()
        engine.add_rule(PriorityRule("low", lambda r: r.prediction.label == "txt", priority=1))
        engine.add_rule(PriorityRule("high", lambda r: r.prediction.label == "pdf", priority=10))
        r_pdf = _mock_result("pdf")
        r_txt = _mock_result("txt")
        assert engine.select([r_txt, r_pdf]) is r_pdf

    def test_select_all_matching_deduplicates(self):
        engine = PriorityEngine()
        engine.add_rule(PriorityRule("any", lambda r: True, priority=1))
        r1 = _mock_result("pdf")
        r2 = _mock_result("txt")
        matched = engine.select_all_matching([r1, r2])
        assert len(matched) == 2
        assert r1 in matched and r2 in matched


# --- PriorityMagika ---

@pytest.fixture
def mock_engine_a():
    e = MagicMock()
    e.identify_bytes.return_value = _mock_result("pdf", 0.95)
    e.identify_path.return_value = _mock_result("pdf", 0.95)
    e.identify_paths.return_value = [_mock_result("pdf", 0.95)]
    return e


@pytest.fixture
def mock_engine_b():
    e = MagicMock()
    e.identify_bytes.return_value = _mock_result("txt", 0.70)
    e.identify_path.return_value = _mock_result("txt", 0.70)
    e.identify_paths.return_value = [_mock_result("txt", 0.70)]
    return e


def test_no_engines_raises():
    with pytest.raises(ValueError):
        PriorityMagika(engines=[])


def test_identify_bytes_selects_via_priority(mock_engine_a, mock_engine_b):
    pe = PriorityEngine()
    pe.add_rule(PriorityRule("prefer_pdf", lambda r: r.prediction.label == "pdf", priority=10))
    engine = PriorityMagika([mock_engine_a, mock_engine_b], pe)
    result = engine.identify_bytes(b"content")
    assert result.prediction.label == "pdf"


def test_identify_paths_returns_correct_count(mock_engine_a, mock_engine_b):
    mock_engine_a.identify_paths.return_value = [_mock_result("pdf"), _mock_result("pdf")]
    mock_engine_b.identify_paths.return_value = [_mock_result("txt"), _mock_result("txt")]
    engine = PriorityMagika([mock_engine_a, mock_engine_b])
    results = engine.identify_paths([Path("a"), Path("b")])
    assert len(results) == 2


def test_identify_paths_empty_returns_empty(mock_engine_a):
    engine = PriorityMagika([mock_engine_a])
    assert engine.identify_paths([]) == []
