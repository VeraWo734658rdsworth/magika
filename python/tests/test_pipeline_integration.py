"""Integration tests: Pipeline + PipelineBuilder with realistic wrappers."""
from __future__ import annotations

from pathlib import Path
from typing import List
from unittest.mock import MagicMock

from magika.pipeline import Pipeline
from magika.pipeline_builder import PipelineBuilder
from magika.prediction import MagikaResult


def _make_result(label: str) -> MagicMock:
    r = MagicMock(spec=MagikaResult)
    r.dl = MagicMock()
    r.dl.ct = MagicMock()
    r.dl.ct.label = label
    return r


class _RecordingEngine:
    """Thin wrapper that records calls and delegates to inner."""

    def __init__(self, inner, name: str) -> None:
        self._inner = inner
        self.name = name
        self.calls: List[str] = []

    def identify_bytes(self, content: bytes) -> MagikaResult:
        self.calls.append("bytes")
        return self._inner.identify_bytes(content)

    def identify_path(self, path: Path) -> MagikaResult:
        self.calls.append("path")
        return self._inner.identify_path(path)

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        self.calls.append("paths")
        return self._inner.identify_paths(paths)


def _base_engine(label: str = "text") -> MagicMock:
    m = MagicMock()
    result = _make_result(label)
    m.identify_bytes.return_value = result
    m.identify_path.return_value = result
    m.identify_paths.return_value = [result, result]
    return m


def test_recording_wrappers_all_called():
    base = _base_engine("pdf")
    r1 = _RecordingEngine(base, "audit")
    r2 = _RecordingEngine(base, "filter")
    pipeline = PipelineBuilder(r1).then(r2).build()

    pipeline.identify_bytes(b"%PDF")
    assert "bytes" in r1.calls
    assert "bytes" in r2.calls


def test_pipeline_final_result_is_last_stage():
    base = _base_engine("python")
    r1 = _RecordingEngine(base, "first")
    r2 = _RecordingEngine(base, "second")
    pipeline = Pipeline([r1, r2])
    result = pipeline.identify_bytes(b"#!/usr/bin/env python")
    assert result.dl.ct.label == "python"


def test_identify_paths_integration():
    base = _base_engine("json")
    r1 = _RecordingEngine(base, "a")
    pipeline = PipelineBuilder(r1).build()
    paths = [Path("a.json"), Path("b.json")]
    results = pipeline.identify_paths(paths)
    assert len(results) == 2
    assert all(r.dl.ct.label == "json" for r in results)
    assert "paths" in r1.calls
