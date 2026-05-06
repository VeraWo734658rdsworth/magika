"""Unit tests for magika.explain_magika.ExplainMagika."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magika.explain import PredictionExplanation
from magika.explain_magika import ExplainMagika


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_result(label: str = "python", score: float = 0.95, group: str = "code"):
    output = MagicMock()
    output.ct_label = label
    output.score = score
    output.group = group
    r = MagicMock()
    r.output = output
    return r


@pytest.fixture()
def mock_magika():
    m = MagicMock()
    m.identify_bytes.return_value = _mock_result()
    m.identify_path.return_value = _mock_result()
    m.identify_paths.return_value = [_mock_result(), _mock_result(label="pdf")]
    return m


@pytest.fixture()
def engine(mock_magika):
    return ExplainMagika(magika=mock_magika)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestExplainMagika:
    def test_identify_bytes_returns_tuple(self, engine):
        result, explanation = engine.identify_bytes(b"print('hello')")
        assert explanation is not None
        assert isinstance(explanation, PredictionExplanation)

    def test_identify_path_returns_tuple(self, engine, tmp_path):
        p = tmp_path / "sample.py"
        p.write_bytes(b"print('hi')")
        result, explanation = engine.identify_path(p)
        assert isinstance(explanation, PredictionExplanation)

    def test_identify_paths_length(self, engine, tmp_path):
        paths = [tmp_path / "a.py", tmp_path / "b.pdf"]
        pairs = engine.identify_paths(paths)
        assert len(pairs) == 2

    def test_identify_paths_all_explanations(self, engine, tmp_path):
        paths = [tmp_path / "a.py", tmp_path / "b.pdf"]
        pairs = engine.identify_paths(paths)
        for _, exp in pairs:
            assert isinstance(exp, PredictionExplanation)

    def test_explain_bytes_convenience(self, engine):
        exp = engine.explain_bytes(b"data")
        assert isinstance(exp, PredictionExplanation)

    def test_explain_path_convenience(self, engine, tmp_path):
        p = tmp_path / "x.py"
        p.write_bytes(b"x=1")
        exp = engine.explain_path(p)
        assert isinstance(exp, PredictionExplanation)

    def test_default_magika_created_when_none(self):
        with patch("magika.explain_magika.Magika") as MockMagika:
            MockMagika.return_value = MagicMock()
            em = ExplainMagika()
            MockMagika.assert_called_once()
