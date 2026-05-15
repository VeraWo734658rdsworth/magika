"""Tests for pipeline_builder.py"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from magika.pipeline import Pipeline, PipelineError
from magika.pipeline_builder import PipelineBuilder


def _mock_engine() -> MagicMock:
    m = MagicMock()
    result = MagicMock()
    m.identify_bytes.return_value = result
    m.identify_path.return_value = result
    m.identify_paths.return_value = [result]
    return m


def test_builder_rejects_non_magika_like_first():
    with pytest.raises(PipelineError):
        PipelineBuilder(object())  # type: ignore


def test_builder_rejects_non_magika_like_then():
    builder = PipelineBuilder(_mock_engine())
    with pytest.raises(PipelineError):
        builder.then(object())  # type: ignore


def test_build_returns_pipeline():
    engine = _mock_engine()
    pipeline = PipelineBuilder(engine).build()
    assert isinstance(pipeline, Pipeline)


def test_chaining_adds_stages():
    a = _mock_engine()
    b = _mock_engine()
    c = _mock_engine()
    builder = PipelineBuilder(a).then(b).then(c)
    assert builder.stage_count == 3


def test_build_preserves_order():
    a = _mock_engine()
    b = _mock_engine()
    pipeline = PipelineBuilder(a).then(b).build()
    assert pipeline.head is a
    assert pipeline.tail is b


def test_then_returns_self_for_fluent_chaining():
    a = _mock_engine()
    b = _mock_engine()
    builder = PipelineBuilder(a)
    returned = builder.then(b)
    assert returned is builder


def test_single_stage_pipeline():
    engine = _mock_engine()
    pipeline = PipelineBuilder(engine).build()
    assert len(pipeline) == 1


def test_repr_contains_builder():
    engine = _mock_engine()
    builder = PipelineBuilder(engine)
    assert "PipelineBuilder" in repr(builder)
