"""Unit tests for python/magika/label_map_magika.py."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.label_map import LabelMap
from magika.label_map_magika import LabelMapMagika


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_result(label: str) -> MagicMock:
    result = MagicMock()
    result.prediction.output.ct_label = label
    return result


@pytest.fixture()
def label_map() -> LabelMap:
    return LabelMap.from_dict({"javascript": "js", "typescript": "ts"})


@pytest.fixture()
def mock_magika() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def engine(mock_magika, label_map) -> LabelMapMagika:
    return LabelMapMagika(inner=mock_magika, label_map=label_map)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_label_map_property(engine, label_map):
    assert engine.label_map is label_map


def test_identify_bytes_remaps_known_label(engine, mock_magika):
    mock_magika.identify_bytes.return_value = _mock_result("javascript")
    result = engine.identify_bytes(b"console.log('hi')")
    assert result.prediction.output.ct_label == "js"


def test_identify_bytes_no_remap_for_unknown_label(engine, mock_magika):
    mock_magika.identify_bytes.return_value = _mock_result("python")
    result = engine.identify_bytes(b"print('hi')")
    assert result.prediction.output.ct_label == "python"


def test_identify_path_remaps(engine, mock_magika, tmp_path):
    p = tmp_path / "app.ts"
    p.write_text("const x = 1;")
    mock_magika.identify_path.return_value = _mock_result("typescript")
    result = engine.identify_path(p)
    assert result.prediction.output.ct_label == "ts"


def test_identify_paths_remaps_each(engine, mock_magika, tmp_path):
    paths = [tmp_path / "a.js", tmp_path / "b.ts"]
    mock_magika.identify_paths.return_value = [
        _mock_result("javascript"),
        _mock_result("typescript"),
    ]
    results = engine.identify_paths(paths)
    assert results[0].prediction.output.ct_label == "js"
    assert results[1].prediction.output.ct_label == "ts"


def test_identify_paths_preserves_unmapped(engine, mock_magika, tmp_path):
    paths = [tmp_path / "data.csv"]
    mock_magika.identify_paths.return_value = [_mock_result("csv")]
    results = engine.identify_paths(paths)
    assert results[0].prediction.output.ct_label == "csv"


def test_inner_called_once_for_identify_bytes(engine, mock_magika):
    mock_magika.identify_bytes.return_value = _mock_result("pdf")
    engine.identify_bytes(b"%PDF")
    mock_magika.identify_bytes.assert_called_once_with(b"%PDF")
