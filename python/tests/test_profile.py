"""Tests for profile.py and profile_magika.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magika.profile import ProfileEntry, ProfilingSession, Timer
from magika.profile_magika import ProfileMagika


# ---------------------------------------------------------------------------
# Timer
# ---------------------------------------------------------------------------

def test_timer_records_positive_elapsed():
    with Timer() as t:
        _ = sum(range(1000))
    assert t.elapsed_ms >= 0.0


def test_timer_elapsed_is_float():
    with Timer() as t:
        pass
    assert isinstance(t.elapsed_ms, float)


# ---------------------------------------------------------------------------
# ProfileEntry
# ---------------------------------------------------------------------------

def test_profile_entry_to_dict_keys():
    entry = ProfileEntry(path=Path("/tmp/foo.py"), label="python", elapsed_ms=1.23)
    d = entry.to_dict()
    assert set(d.keys()) == {"path", "label", "elapsed_ms"}


def test_profile_entry_to_dict_none_path():
    entry = ProfileEntry(path=None, label="binary", elapsed_ms=0.5)
    assert entry.to_dict()["path"] is None


def test_profile_entry_repr_contains_label():
    entry = ProfileEntry(path=None, label="pdf", elapsed_ms=2.0)
    assert "pdf" in repr(entry)


# ---------------------------------------------------------------------------
# ProfilingSession
# ---------------------------------------------------------------------------

def test_session_starts_empty():
    s = ProfilingSession()
    assert len(s) == 0
    assert s.total_ms() == 0.0
    assert s.average_ms() == 0.0
    assert s.slowest() is None


def test_session_record_increments_length():
    s = ProfilingSession()
    s.record(path=None, label="txt", elapsed_ms=1.0)
    s.record(path=None, label="pdf", elapsed_ms=3.0)
    assert len(s) == 2


def test_session_total_and_average():
    s = ProfilingSession()
    s.record(path=None, label="a", elapsed_ms=2.0)
    s.record(path=None, label="b", elapsed_ms=4.0)
    assert s.total_ms() == pytest.approx(6.0)
    assert s.average_ms() == pytest.approx(3.0)


def test_session_slowest():
    s = ProfilingSession()
    s.record(path=None, label="fast", elapsed_ms=1.0)
    s.record(path=None, label="slow", elapsed_ms=9.0)
    assert s.slowest().label == "slow"


def test_session_clear():
    s = ProfilingSession()
    s.record(path=None, label="x", elapsed_ms=1.0)
    s.clear()
    assert len(s) == 0


# ---------------------------------------------------------------------------
# ProfileMagika
# ---------------------------------------------------------------------------

def _mock_result(label: str) -> MagicMock:
    result = MagicMock()
    result.prediction.label = label
    return result


@pytest.fixture()
def mock_magika():
    m = MagicMock()
    m.identify_bytes.return_value = _mock_result("python")
    m.identify_path.return_value = _mock_result("pdf")
    m.identify_paths.return_value = [_mock_result("txt"), _mock_result("html")]
    return m


def test_profile_magika_identify_bytes_records_entry(mock_magika):
    pm = ProfileMagika(mock_magika)
    pm.identify_bytes(b"hello")
    assert len(pm.session) == 1
    assert pm.session.entries[0].label == "python"
    assert pm.session.entries[0].path is None


def test_profile_magika_identify_path_records_entry(mock_magika, tmp_path):
    p = tmp_path / "file.pdf"
    p.write_bytes(b"%PDF")
    pm = ProfileMagika(mock_magika)
    pm.identify_path(p)
    assert len(pm.session) == 1
    assert pm.session.entries[0].path == p


def test_profile_magika_identify_paths_records_all(mock_magika, tmp_path):
    paths = [tmp_path / "a.txt", tmp_path / "b.html"]
    pm = ProfileMagika(mock_magika)
    pm.identify_paths(paths)
    assert len(pm.session) == 2


def test_profile_magika_clear_profile(mock_magika):
    pm = ProfileMagika(mock_magika)
    pm.identify_bytes(b"data")
    pm.clear_profile()
    assert len(pm.session) == 0
