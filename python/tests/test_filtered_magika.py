"""Tests for FilteredMagika."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magika.filter import ResultFilter
from magika.filtered_magika import FilteredMagika


def _make_result(label: str, group: str = "code", score: float = 0.99) -> MagicMock:
    info = MagicMock(label=label, group=group, mime_type=f"text/x-{label}")
    pred = MagicMock(content_type_info=info, score=score)
    r = MagicMock()
    r.prediction = pred
    return r


@pytest.fixture()
def mock_magika():
    return MagicMock()


def test_identify_bytes_passes_filter(mock_magika):
    mock_magika.identify_bytes.return_value = _make_result("python")
    fm = FilteredMagika(ResultFilter(labels=["python"]), magika=mock_magika)
    results = fm.identify_bytes(b"print('hi')")
    assert len(results) == 1


def test_identify_bytes_blocks_filter(mock_magika):
    mock_magika.identify_bytes.return_value = _make_result("jpeg", group="image")
    fm = FilteredMagika(ResultFilter(labels=["python"]), magika=mock_magika)
    results = fm.identify_bytes(b"\xff\xd8")
    assert results == []


def test_identify_path_passes_filter(mock_magika, tmp_path):
    p = tmp_path / "script.py"
    p.write_text("x = 1")
    mock_magika.identify_path.return_value = _make_result("python")
    fm = FilteredMagika(ResultFilter(groups=["code"]), magika=mock_magika)
    assert len(fm.identify_path(p)) == 1


def test_identify_paths_filters_subset(mock_magika, tmp_path):
    paths = [tmp_path / f"f{i}" for i in range(3)]
    for p in paths:
        p.touch()
    mock_magika.identify_paths.return_value = [
        _make_result("python", group="code"),
        _make_result("jpeg", group="image"),
        _make_result("shell", group="code"),
    ]
    fm = FilteredMagika(ResultFilter(groups=["code"]), magika=mock_magika)
    results = fm.identify_paths(paths)
    assert len(results) == 2


def test_active_filter_property(mock_magika):
    f = ResultFilter(min_score=0.8)
    fm = FilteredMagika(f, magika=mock_magika)
    assert fm.active_filter is f


def test_default_magika_instantiated():
    with patch("magika.filtered_magika.Magika") as MockMagika:
        fm = FilteredMagika(ResultFilter())
        MockMagika.assert_called_once()
