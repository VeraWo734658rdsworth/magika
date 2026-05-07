"""Tests for python/magika/normalize.py."""

from __future__ import annotations

import pytest

from magika.normalize import (
    NormalizationError,
    NormalizedLabel,
    NormalizedMime,
    normalize_label,
    normalize_mime,
    try_normalize_label,
    try_normalize_mime,
)


# ---------------------------------------------------------------------------
# NormalizedLabel
# ---------------------------------------------------------------------------

class TestNormalizedLabel:
    def test_valid_simple(self):
        lbl = NormalizedLabel("python")
        assert str(lbl) == "python"

    def test_valid_with_special_chars(self):
        lbl = NormalizedLabel("c++")
        assert lbl.value == "c++"

    def test_empty_raises(self):
        with pytest.raises(NormalizationError):
            NormalizedLabel("")

    def test_uppercase_raises(self):
        with pytest.raises(NormalizationError):
            NormalizedLabel("Python")

    def test_space_raises(self):
        with pytest.raises(NormalizationError):
            NormalizedLabel("my label")

    def test_starts_with_digit_ok(self):
        lbl = NormalizedLabel("7z")
        assert lbl.value == "7z"


# ---------------------------------------------------------------------------
# NormalizedMime
# ---------------------------------------------------------------------------

class TestNormalizedMime:
    def test_valid_mime(self):
        m = NormalizedMime("text/plain")
        assert m.media_type == "text"
        assert m.subtype == "plain"

    def test_str(self):
        m = NormalizedMime("application/json")
        assert str(m) == "application/json"

    def test_empty_raises(self):
        with pytest.raises(NormalizationError):
            NormalizedMime("")

    def test_missing_slash_raises(self):
        with pytest.raises(NormalizationError):
            NormalizedMime("textplain")

    def test_double_slash_raises(self):
        with pytest.raises(NormalizationError):
            NormalizedMime("text/plain/extra")

    def test_empty_subtype_raises(self):
        with pytest.raises(NormalizationError):
            NormalizedMime("text/")


# ---------------------------------------------------------------------------
# normalize_label / normalize_mime helpers
# ---------------------------------------------------------------------------

def test_normalize_label_strips_and_lowercases():
    lbl = normalize_label("  Python  ")
    assert lbl.value == "python"


def test_normalize_mime_strips_and_lowercases():
    m = normalize_mime("  Text/HTML  ")
    assert m.value == "text/html"


def test_try_normalize_label_valid():
    assert try_normalize_label("pdf") is not None


def test_try_normalize_label_invalid_returns_none():
    assert try_normalize_label("bad label!") is None


def test_try_normalize_mime_valid():
    result = try_normalize_mime("image/png")
    assert result is not None
    assert result.media_type == "image"


def test_try_normalize_mime_invalid_returns_none():
    assert try_normalize_mime("not-a-mime") is None
