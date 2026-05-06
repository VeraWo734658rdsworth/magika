"""Tests for magika.filter."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.filter import (
    ResultFilter,
    filter_by_group,
    filter_by_label,
    filter_by_min_score,
)


def _make_result(label: str, mime: str, group: str, score: float) -> MagicMock:
    info = MagicMock()
    info.label = label
    info.mime_type = mime
    info.group = group

    prediction = MagicMock()
    prediction.content_type_info = info
    prediction.score = score

    result = MagicMock()
    result.prediction = prediction
    return result


RESULTS = [
    _make_result("python", "text/x-python", "code", 0.99),
    _make_result("pdf", "application/pdf", "document", 0.95),
    _make_result("jpeg", "image/jpeg", "image", 0.87),
    _make_result("shell", "text/x-shellscript", "code", 0.60),
]


def test_filter_by_label_single():
    out = filter_by_label(RESULTS, ["python"])
    assert len(out) == 1
    assert out[0].prediction.content_type_info.label == "python"


def test_filter_by_label_multiple():
    out = filter_by_label(RESULTS, ["python", "pdf"])
    assert len(out) == 2


def test_filter_by_label_no_match():
    assert filter_by_label(RESULTS, ["zip"]) == []


def test_filter_by_group():
    out = filter_by_group(RESULTS, ["code"])
    assert len(out) == 2
    labels = {r.prediction.content_type_info.label for r in out}
    assert labels == {"python", "shell"}


def test_filter_by_min_score_high():
    out = filter_by_min_score(RESULTS, 0.90)
    assert len(out) == 2


def test_filter_by_min_score_zero():
    assert len(filter_by_min_score(RESULTS, 0.0)) == len(RESULTS)


def test_result_filter_combined():
    f = ResultFilter(groups=["code"], min_score=0.90)
    out = f.apply(RESULTS)
    assert len(out) == 1
    assert out[0].prediction.content_type_info.label == "python"


def test_result_filter_mime():
    f = ResultFilter(mime_types=["image/jpeg"])
    out = f.apply(RESULTS)
    assert len(out) == 1


def test_result_filter_empty_criteria_passes_all():
    f = ResultFilter()
    assert len(f.apply(RESULTS)) == len(RESULTS)
