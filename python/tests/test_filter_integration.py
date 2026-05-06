"""Integration-style tests combining ResultFilter with realistic result shapes."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from magika.filter import ResultFilter, filter_by_label, filter_by_min_score


def _r(label, group, mime, score):
    info = MagicMock(label=label, group=group, mime_type=mime)
    pred = MagicMock(content_type_info=info, score=score)
    res = MagicMock()
    res.prediction = pred
    return res


MIXED = [
    _r("python", "code", "text/x-python", 0.98),
    _r("javascript", "code", "text/javascript", 0.91),
    _r("pdf", "document", "application/pdf", 0.99),
    _r("png", "image", "image/png", 0.75),
    _r("unknown", "unknown", "application/octet-stream", 0.40),
]


def test_combined_group_and_score():
    f = ResultFilter(groups=["code"], min_score=0.95)
    out = f.apply(MIXED)
    assert len(out) == 1
    assert out[0].prediction.content_type_info.label == "python"


def test_combined_label_and_mime():
    f = ResultFilter(labels=["pdf"], mime_types=["application/pdf"])
    out = f.apply(MIXED)
    assert len(out) == 1


def test_label_and_mime_mismatch_returns_empty():
    # label matches pdf but mime doesn't → no results
    f = ResultFilter(labels=["pdf"], mime_types=["image/png"])
    assert f.apply(MIXED) == []


def test_high_confidence_only():
    out = filter_by_min_score(MIXED, 0.90)
    labels = {r.prediction.content_type_info.label for r in out}
    assert labels == {"python", "javascript", "pdf"}


def test_filter_preserves_order():
    out = filter_by_label(MIXED, ["pdf", "python", "png"])
    returned_labels = [r.prediction.content_type_info.label for r in out]
    assert returned_labels == ["python", "pdf", "png"]


def test_empty_input():
    assert ResultFilter(groups=["code"]).apply([]) == []
