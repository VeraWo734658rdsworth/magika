"""Tests for python/magika/audit.py and audit_magika.py."""

from __future__ import annotations

import io
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magika.audit import AuditEntry, AuditLogger, load_audit_log
from magika.audit_magika import AuditMagika


def _mock_result(label: str = "python", score: float = 0.99) -> MagicMock:
    result = MagicMock()
    result.prediction.label = label
    result.prediction.score = score
    return result


# ---------------------------------------------------------------------------
# AuditEntry
# ---------------------------------------------------------------------------

class TestAuditEntry:
    def test_to_dict_contains_required_keys(self):
        entry = AuditEntry(path="/tmp/foo.py", label="python", score=0.95, timestamp=1_000_000.0)
        d = entry.to_dict()
        assert set(d.keys()) == {"path", "label", "score", "timestamp"}

    def test_score_rounded(self):
        entry = AuditEntry(path=None, label="text", score=0.123456789, timestamp=0.0)
        assert len(str(entry.to_dict()["score"]).split(".")[-1]) <= 6

    def test_repr_contains_label(self):
        entry = AuditEntry(path=None, label="pdf", score=0.8, timestamp=0.0)
        assert "pdf" in repr(entry)


# ---------------------------------------------------------------------------
# AuditLogger
# ---------------------------------------------------------------------------

class TestAuditLogger:
    def test_log_result_increments_count(self):
        stream = io.StringIO()
        logger = AuditLogger(stream)
        logger.log_result(_mock_result())
        assert logger.count == 1

    def test_log_result_writes_valid_json(self):
        stream = io.StringIO()
        logger = AuditLogger(stream)
        logger.log_result(_mock_result(label="pdf", score=0.75), path="/a/b.pdf")
        stream.seek(0)
        data = json.loads(stream.read())
        assert data["label"] == "pdf"
        assert data["path"] == "/a/b.pdf"

    def test_log_results_multiple(self):
        stream = io.StringIO()
        logger = AuditLogger(stream)
        results = [_mock_result("python"), _mock_result("html"), _mock_result("jpeg")]
        entries = logger.log_results(results, paths=["/a", "/b", "/c"])
        assert len(entries) == 3
        assert logger.count == 3

    def test_log_results_no_paths(self):
        stream = io.StringIO()
        logger = AuditLogger(stream)
        results = [_mock_result(), _mock_result()]
        entries = logger.log_results(results)
        assert all(e.path is None for e in entries)


# ---------------------------------------------------------------------------
# load_audit_log round-trip
# ---------------------------------------------------------------------------

def test_round_trip():
    stream = io.StringIO()
    logger = AuditLogger(stream)
    logger.log_result(_mock_result(label="zip", score=0.88), path="/x/y.zip")
    logger.log_result(_mock_result(label="elf", score=0.99), path="/bin/ls")
    stream.seek(0)
    entries = load_audit_log(stream)
    assert len(entries) == 2
    assert entries[0].label == "zip"
    assert entries[1].label == "elf"


# ---------------------------------------------------------------------------
# AuditMagika
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_magika():
    m = MagicMock()
    m.identify_bytes.return_value = _mock_result("python", 0.97)
    m.identify_path.return_value = _mock_result("python", 0.97)
    m.identify_paths.return_value = [_mock_result("python", 0.97)]
    return m


class TestAuditMagika:
    def test_identify_bytes_logs_entry(self, mock_magika):
        stream = io.StringIO()
        engine = AuditMagika(mock_magika, stream)
        engine.identify_bytes(b"print('hi')")
        assert engine.total_logged == 1

    def test_identify_path_logs_path(self, mock_magika, tmp_path):
        p = tmp_path / "script.py"
        p.write_bytes(b"x = 1")
        stream = io.StringIO()
        engine = AuditMagika(mock_magika, stream)
        engine.identify_path(p)
        stream.seek(0)
        data = json.loads(stream.read())
        assert data["path"] == str(p)

    def test_identify_paths_logs_all(self, mock_magika):
        mock_magika.identify_paths.return_value = [_mock_result(), _mock_result()]
        stream = io.StringIO()
        engine = AuditMagika(mock_magika, stream)
        engine.identify_paths([Path("/a"), Path("/b")])
        assert engine.total_logged == 2
