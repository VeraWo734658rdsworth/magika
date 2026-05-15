"""Tests for pipeline.py"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from magika.pipeline import Pipeline, PipelineError


def _mock_engine(label: str = "text") -> MagicMock:
    m = MagicMock()
    result = MagicMock()
    result.dl.ct.label = label
    m.identify_bytes.return_value = result
    m.identify_path.return_value = result
    m.identify_paths.return_value = [result]
    return m


def test_pipeline_requires_at_least_one_stage():
    with pytest.raises(PipelineError):
        Pipeline([])


def test_pipeline_rejects_non_magika_like():
    with pytest.raises(PipelineError):
        Pipeline([object()])  # type: ignore


def test_single_stage_identify_bytes():
    engine = _mock_engine("pdf")
    p = Pipeline([engine])
    result = p.identify_bytes(b"%PDF")
    engine.identify_bytes.assert_called_once_with(b"%PDF")
    assert result.dl.ct.label == "pdf"


def test_single_stage_identify_path():
    engine = _mock_engine("python")
    p = Pipeline([engine])
    path = Path("script.py")
    result = p.identify_path(path)
    engine.identify_path.assert_called_once_with(path)
    assert result.dl.ct.label == "python"


def test_all_stages_called_for_identify_bytes():
    a = _mock_engine("text")
    b = _mock_engine("pdf")
    p = Pipeline([a, b])
    content = b"hello"
    result = p.identify_bytes(content)
    a.identify_bytes.assert_called_once_with(content)
    b.identify_bytes.assert_called_once_with(content)
    assert result.dl.ct.label == "pdf"  # last stage wins


def test_identify_paths_returns_last_stage_results():
    a = _mock_engine("text")
    b = _mock_engine("json")
    p = Pipeline([a, b])
    paths = [Path("a.txt"), Path("b.json")]
    results = p.identify_paths(paths)
    assert all(r.dl.ct.label == "json" for r in results)


def test_len_reflects_stage_count():
    stages = [_mock_engine() for _ in range(3)]
    p = Pipeline(stages)
    assert len(p) == 3


def test_head_and_tail():
    a = _mock_engine()
    b = _mock_engine()
    c = _mock_engine()
    p = Pipeline([a, b, c])
    assert p.head is a
    assert p.tail is c


def test_repr_contains_class_names():
    a = _mock_engine()
    p = Pipeline([a])
    assert "Pipeline" in repr(p)
