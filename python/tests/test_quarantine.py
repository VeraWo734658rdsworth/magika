"""Tests for quarantine.py and quarantine_magika.py."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.quarantine import (
    QuarantineEntry,
    QuarantineError,
    QuarantinePolicy,
    apply_quarantine,
)
from magika.quarantine_magika import QuarantineMagika


def _mock_result(label: str, mime: str = "application/octet-stream", score: float = 0.99):
    result = MagicMock()
    result.prediction.label = label
    result.prediction.mime_type = mime
    result.prediction.score = score
    return result


# --- QuarantinePolicy ---

def test_empty_policy_raises():
    with pytest.raises(QuarantineError):
        QuarantinePolicy()


def test_from_labels_normalises_case():
    policy = QuarantinePolicy.from_labels(["EXE", " Pdf "])
    assert "exe" in policy.labels
    assert "pdf" in policy.labels


def test_from_mime_types_normalises_case():
    policy = QuarantinePolicy.from_mime_types(["Application/X-Executable"])
    assert "application/x-executable" in policy.mime_types


def test_should_quarantine_by_label():
    policy = QuarantinePolicy.from_labels(["exe"])
    result = _mock_result("exe")
    assert policy.should_quarantine(result) is True


def test_should_not_quarantine_clean_label():
    policy = QuarantinePolicy.from_labels(["exe"])
    result = _mock_result("pdf")
    assert policy.should_quarantine(result) is False


def test_should_quarantine_by_mime():
    policy = QuarantinePolicy.from_mime_types(["application/x-dosexec"])
    result = _mock_result("exe", mime="application/x-dosexec")
    assert policy.should_quarantine(result) is True


# --- apply_quarantine ---

def test_apply_quarantine_splits_correctly():
    policy = QuarantinePolicy.from_labels(["exe"])
    results = [_mock_result("pdf"), _mock_result("exe"), _mock_result("txt")]
    clean, flagged = apply_quarantine(results, policy)
    assert len(clean) == 2
    assert len(flagged) == 1
    assert flagged[0].result.prediction.label == "exe"


def test_apply_quarantine_empty_input():
    policy = QuarantinePolicy.from_labels(["exe"])
    clean, flagged = apply_quarantine([], policy)
    assert clean == []
    assert flagged == []


def test_quarantine_entry_to_dict_keys():
    policy = QuarantinePolicy.from_labels(["exe"])
    result = _mock_result("exe", score=0.987654)
    _, flagged = apply_quarantine([result], policy)
    d = flagged[0].to_dict()
    assert set(d.keys()) == {"label", "mime_type", "score", "reason"}
    assert d["score"] == round(0.987654, 4)


def test_quarantine_entry_repr_contains_label():
    result = _mock_result("exe")
    entry = QuarantineEntry(result=result, reason="label 'exe' matched quarantine policy")
    assert "exe" in repr(entry)


# --- QuarantineMagika ---

@pytest.fixture()
def mock_magika():
    m = MagicMock()
    m.identify_bytes.side_effect = lambda b: _mock_result("exe")
    m.identify_path.side_effect = lambda p: _mock_result("pdf")
    m.identify_paths.side_effect = lambda ps: [_mock_result("exe"), _mock_result("txt")]
    return m


@pytest.fixture()
def engine(mock_magika):
    policy = QuarantinePolicy.from_labels(["exe"])
    return QuarantineMagika(inner=mock_magika, policy=policy)


def test_identify_bytes_quarantines_exe(engine):
    engine.identify_bytes(b"MZ...")
    assert len(engine.quarantined) == 1
    assert engine.quarantined[0].result.prediction.label == "exe"


def test_identify_path_does_not_quarantine_pdf(engine):
    engine.identify_path(Path("/tmp/doc.pdf"))
    assert len(engine.quarantined) == 0


def test_identify_paths_filters_quarantined(engine):
    results = engine.identify_paths([Path("/a"), Path("/b")])
    assert len(results) == 1
    assert results[0].prediction.label == "txt"
    assert len(engine.quarantined) == 1


def test_clear_quarantine_resets_log(engine):
    engine.identify_bytes(b"MZ...")
    assert len(engine.quarantined) == 1
    engine.clear_quarantine()
    assert len(engine.quarantined) == 0
