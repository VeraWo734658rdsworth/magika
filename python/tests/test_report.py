"""Unit tests for python/magika/report.py."""
from __future__ import annotations

import json

import pytest

from magika.report import Report, ReportEntry


def _make_entry(label: str = "python", group: str = "code", score: float = 0.99) -> ReportEntry:
    return ReportEntry(
        path="/tmp/foo.py",
        label=label,
        mime_type="text/x-python",
        score=score,
        group=group,
    )


def test_entry_to_dict_keys():
    e = _make_entry()
    d = e.to_dict()
    assert set(d.keys()) == {"path", "label", "mime_type", "score", "group"}


def test_entry_score_rounded():
    e = _make_entry(score=0.123456789)
    assert e.to_dict()["score"] == round(0.123456789, 4)


def test_entry_none_path():
    e = ReportEntry(path=None, label="pdf", mime_type="application/pdf", score=0.9, group="document")
    assert e.to_dict()["path"] is None


def test_empty_report_length():
    r = Report()
    assert len(r) == 0


def test_report_to_dict_structure():
    r = Report()
    d = r.to_dict()
    assert d["total"] == 0
    assert d["entries"] == []


def test_report_to_json_valid():
    r = Report()
    s = r.to_json()
    parsed = json.loads(s)
    assert "total" in parsed


def test_label_counts_empty():
    r = Report()
    assert r.label_counts() == {}


def test_label_counts_multiple_entries():
    r = Report()
    r.entries.append(_make_entry(label="python"))
    r.entries.append(_make_entry(label="python"))
    r.entries.append(_make_entry(label="pdf", group="document"))
    counts = r.label_counts()
    assert counts["python"] == 2
    assert counts["pdf"] == 1


def test_filter_by_group_returns_subset():
    r = Report()
    r.entries.append(_make_entry(label="python", group="code"))
    r.entries.append(_make_entry(label="pdf", group="document"))
    filtered = r.filter_by_group("code")
    assert len(filtered) == 1
    assert filtered.entries[0].label == "python"


def test_filter_by_group_no_match_returns_empty():
    r = Report()
    r.entries.append(_make_entry(group="code"))
    assert len(r.filter_by_group("archive")) == 0


def test_filter_does_not_mutate_original():
    r = Report()
    r.entries.append(_make_entry(group="code"))
    r.entries.append(_make_entry(group="document"))
    _ = r.filter_by_group("code")
    assert len(r) == 2
