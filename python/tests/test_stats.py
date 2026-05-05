"""Tests for magika.stats module."""

from unittest.mock import MagicMock

import pytest

from magika.stats import PredictionStats


def _make_result(label: str, group: str, score: float) -> MagicMock:
    result = MagicMock()
    result.output.ct_label = label
    result.output.group = group
    result.output.score = score
    return result


def test_initial_state():
    stats = PredictionStats()
    assert stats.total == 0
    assert stats.average_score == 0.0
    assert stats.most_common_label is None
    assert stats.most_common_group is None
    assert stats.low_confidence_count == 0


def test_single_update():
    stats = PredictionStats()
    result = _make_result("python", "code", 0.95)
    stats.update(result)

    assert stats.total == 1
    assert stats.label_counts["python"] == 1
    assert stats.group_counts["code"] == 1
    assert abs(stats.average_score - 0.95) < 1e-6
    assert stats.low_confidence_count == 0


def test_low_confidence_tracking():
    stats = PredictionStats(low_confidence_threshold=0.8)
    stats.update(_make_result("unknown", "unknown", 0.5))
    stats.update(_make_result("python", "code", 0.9))

    assert stats.low_confidence_count == 1


def test_update_many():
    stats = PredictionStats()
    results = [
        _make_result("python", "code", 0.9),
        _make_result("python", "code", 0.8),
        _make_result("javascript", "code", 0.7),
    ]
    stats.update_many(results)

    assert stats.total == 3
    assert stats.label_counts["python"] == 2
    assert stats.label_counts["javascript"] == 1
    assert stats.most_common_label == "python"
    assert stats.most_common_group == "code"


def test_average_score():
    stats = PredictionStats()
    stats.update(_make_result("pdf", "document", 1.0))
    stats.update(_make_result("png", "image", 0.5))

    assert abs(stats.average_score - 0.75) < 1e-6


def test_to_dict_keys():
    stats = PredictionStats()
    stats.update(_make_result("html", "markup", 0.88))
    d = stats.to_dict()

    expected_keys = {
        "total", "average_score", "low_confidence_count",
        "low_confidence_threshold", "most_common_label",
        "most_common_group", "label_counts", "group_counts",
    }
    assert set(d.keys()) == expected_keys
    assert d["total"] == 1
    assert d["most_common_label"] == "html"


def test_repr():
    stats = PredictionStats()
    stats.update(_make_result("zip", "archive", 0.99))
    r = repr(stats)
    assert "PredictionStats" in r
    assert "total=1" in r
