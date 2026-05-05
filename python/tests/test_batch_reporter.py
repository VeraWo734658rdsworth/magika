"""Tests for batch_reporter utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple
from unittest.mock import MagicMock

import pytest

from magika.batch_reporter import (
    count_errors,
    print_batch_json_report,
    print_batch_text_report,
    summarize_batch_results,
)
from magika.types import Status


def _make_result(label: str, status: Status = Status.OK) -> MagicMock:
    r = MagicMock()
    r.output.ct_label = label
    r.status = status
    return r


def _pairs(labels, statuses=None) -> List[Tuple[Path, MagicMock]]:
    if statuses is None:
        statuses = [Status.OK] * len(labels)
    return [
        (Path(f"/tmp/f{i}"), _make_result(lbl, st))
        for i, (lbl, st) in enumerate(zip(labels, statuses))
    ]


def test_summarize_empty():
    assert summarize_batch_results([]) == {}


def test_summarize_counts():
    results = _pairs(["text", "pdf", "text", "text", "pdf"])
    summary = summarize_batch_results(results)
    assert summary["text"] == 3
    assert summary["pdf"] == 2


def test_summarize_sorted_descending():
    results = _pairs(["a", "b", "b", "c", "c", "c"])
    summary = summarize_batch_results(results)
    counts = list(summary.values())
    assert counts == sorted(counts, reverse=True)


def test_count_errors_none():
    results = _pairs(["text", "pdf"])
    assert count_errors(results) == 0


def test_count_errors_some():
    results = _pairs(
        ["text", "unknown", "pdf"],
        [Status.OK, Status.ERROR, Status.ERROR],
    )
    assert count_errors(results) == 2


def test_print_text_report_runs(capsys):
    results = _pairs(["text", "pdf", "text"])
    print_batch_text_report(results)
    captured = capsys.readouterr()
    assert "3" in captured.out
    assert "text" in captured.out


def test_print_json_report_valid_json(capsys):
    results = _pairs(["text", "pdf"])
    print_batch_json_report(results)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["total"] == 2
    assert "breakdown" in data
    assert data["errors"] == 0
