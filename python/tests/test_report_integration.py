"""Integration tests exercising Report + ReportMagika together."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from magika.report import Report, ReportEntry
from magika.report_magika import ReportMagika


def _make_result(label: str, group: str = "code", score: float = 0.9) -> MagicMock:
    r = MagicMock()
    r.dl.ct_label = label
    r.output.mime_type = f"text/x-{label}"
    r.output.score = score
    r.output.group = group
    return r


def _make_engine(labels, group="code"):
    inner = MagicMock()
    results = [_make_result(l, group) for l in labels]
    inner.identify_paths.return_value = results
    for r in results:
        inner.identify_bytes.return_value = r
    return ReportMagika(inner), results


def test_json_round_trip():
    engine, _ = _make_engine(["python", "pdf", "zip"], "code")
    paths = [Path(f"/tmp/{i}") for i in range(3)]
    engine.identify_paths(paths)
    serialised = engine.report.to_json()
    parsed = json.loads(serialised)
    assert parsed["total"] == 3
    assert len(parsed["entries"]) == 3


def test_label_counts_after_mixed_calls():
    inner = MagicMock()
    inner.identify_bytes.side_effect = [
        _make_result("python"),
        _make_result("python"),
        _make_result("pdf", "document"),
    ]
    engine = ReportMagika(inner)
    for content in [b"a", b"b", b"c"]:
        engine.identify_bytes(content)
    counts = engine.report.label_counts()
    assert counts["python"] == 2
    assert counts["pdf"] == 1


def test_filter_group_after_identify_paths():
    engine, _ = _make_engine(["python", "shell"], "code")
    inner2 = MagicMock()
    inner2.identify_paths.return_value = [_make_result("pdf", "document")]
    engine2 = ReportMagika(inner2)
    engine.identify_paths([Path("/a"), Path("/b")])
    engine2.identify_paths([Path("/c")])
    # merge entries manually
    combined = Report()
    combined.entries = engine.report.entries + engine2.report.entries
    assert len(combined.filter_by_group("code")) == 2
    assert len(combined.filter_by_group("document")) == 1


def test_clear_and_reuse():
    inner = MagicMock()
    inner.identify_bytes.return_value = _make_result("python")
    engine = ReportMagika(inner)
    engine.identify_bytes(b"x")
    assert len(engine.report) == 1
    engine.clear_report()
    engine.identify_bytes(b"y")
    assert len(engine.report) == 1
    assert engine.report.entries[0].label == "python"
