"""Unit tests for python/magika/report_magika.py."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.report import Report
from magika.report_magika import ReportMagika


def _mock_result(label: str = "python") -> MagicMock:
    result = MagicMock()
    result.dl.ct_label = label
    result.output.mime_type = "text/x-python"
    result.output.score = 0.95
    result.output.group = "code"
    return result


@pytest.fixture()
def mock_magika():
    m = MagicMock()
    m.identify_bytes.return_value = _mock_result()
    m.identify_path.return_value = _mock_result()
    m.identify_paths.return_value = [_mock_result(), _mock_result()]
    return m


@pytest.fixture()
def engine(mock_magika):
    return ReportMagika(mock_magika)


def test_report_initially_empty(engine):
    assert len(engine.report) == 0


def test_identify_bytes_adds_entry(engine):
    engine.identify_bytes(b"print('hello')")
    assert len(engine.report) == 1


def test_identify_path_adds_entry(engine):
    engine.identify_path(Path("/tmp/foo.py"))
    assert len(engine.report) == 1


def test_identify_paths_adds_entries(engine):
    paths = [Path("/tmp/a.py"), Path("/tmp/b.py")]
    engine.identify_paths(paths)
    assert len(engine.report) == 2


def test_identify_bytes_returns_result(engine):
    result = engine.identify_bytes(b"data")
    assert result is not None
    assert result.dl.ct_label == "python"


def test_clear_report_resets_entries(engine):
    engine.identify_bytes(b"data")
    engine.clear_report()
    assert len(engine.report) == 0


def test_report_path_stored_for_identify_path(engine):
    engine.identify_path(Path("/tmp/hello.py"))
    entry = engine.report.entries[0]
    assert entry.path == "/tmp/hello.py"


def test_report_path_none_for_identify_bytes(engine):
    engine.identify_bytes(b"data")
    entry = engine.report.entries[0]
    assert entry.path is None


def test_multiple_calls_accumulate(engine):
    engine.identify_bytes(b"a")
    engine.identify_bytes(b"b")
    engine.identify_path(Path("/tmp/c.py"))
    assert len(engine.report) == 3
