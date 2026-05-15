"""Tests for magika.clamp and ClampMagika."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.clamp import ClampError, ClampPolicy, clamp_result, clamp_score
from magika.clamp_magika import ClampMagika


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_result(score: float):
    """Build a minimal MagikaResult-like mock with the given score."""
    prediction = MagicMock()
    prediction.score = score
    result = MagicMock()
    result.prediction = prediction
    return result


# ---------------------------------------------------------------------------
# ClampPolicy
# ---------------------------------------------------------------------------

def test_default_policy_is_valid():
    p = ClampPolicy()
    assert p.low == 0.0
    assert p.high == 1.0


def test_custom_policy_accepted():
    p = ClampPolicy(low=0.1, high=0.9)
    assert p.low == 0.1
    assert p.high == 0.9


def test_policy_rejects_low_above_high():
    with pytest.raises(ClampError):
        ClampPolicy(low=0.8, high=0.2)


def test_policy_rejects_negative_low():
    with pytest.raises(ClampError):
        ClampPolicy(low=-0.1)


def test_policy_rejects_high_above_one():
    with pytest.raises(ClampError):
        ClampPolicy(high=1.5)


def test_equal_low_and_high_accepted():
    p = ClampPolicy(low=0.5, high=0.5)
    assert p.low == p.high == 0.5


# ---------------------------------------------------------------------------
# clamp_score
# ---------------------------------------------------------------------------

def test_clamp_score_within_range():
    assert clamp_score(0.5, ClampPolicy(low=0.2, high=0.8)) == 0.5


def test_clamp_score_below_low():
    assert clamp_score(0.05, ClampPolicy(low=0.1, high=0.9)) == pytest.approx(0.1)


def test_clamp_score_above_high():
    assert clamp_score(0.99, ClampPolicy(low=0.1, high=0.9)) == pytest.approx(0.9)


def test_clamp_score_at_boundary():
    assert clamp_score(0.0, ClampPolicy()) == 0.0
    assert clamp_score(1.0, ClampPolicy()) == 1.0


# ---------------------------------------------------------------------------
# ClampMagika
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_magika():
    return MagicMock()


@pytest.fixture()
def engine(mock_magika):
    return ClampMagika(mock_magika, ClampPolicy(low=0.1, high=0.9))


def test_policy_property(engine):
    assert engine.policy.low == 0.1
    assert engine.policy.high == 0.9


def test_identify_bytes_clamps_score(mock_magika, engine):
    mock_magika.identify_bytes.return_value = _mock_result(0.99)
    result = engine.identify_bytes(b"data")
    assert result.prediction.score <= 0.9


def test_identify_path_clamps_score(mock_magika, engine):
    mock_magika.identify_path.return_value = _mock_result(0.01)
    result = engine.identify_path(Path("file.txt"))
    assert result.prediction.score >= 0.1


def test_identify_paths_clamps_all(mock_magika, engine):
    mock_magika.identify_paths.return_value = [
        _mock_result(0.0),
        _mock_result(1.0),
        _mock_result(0.5),
    ]
    results = engine.identify_paths([Path("a"), Path("b"), Path("c")])
    scores = [r.prediction.score for r in results]
    assert all(0.1 <= s <= 0.9 for s in scores)


def test_default_policy_is_identity(mock_magika):
    eng = ClampMagika(mock_magika)
    mock_magika.identify_bytes.return_value = _mock_result(0.75)
    result = eng.identify_bytes(b"x")
    assert result.prediction.score == pytest.approx(0.75)
