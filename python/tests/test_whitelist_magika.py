"""Tests for WhitelistMagika and Whitelist."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.whitelist import Whitelist, WhitelistError
from magika.whitelist_magika import WhitelistMagika


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_result(label: str):
    result = MagicMock()
    result.prediction.label = label
    return result


@pytest.fixture()
def whitelist():
    return Whitelist.from_labels(["pdf", "python", "zip"])


@pytest.fixture()
def mock_magika():
    return MagicMock()


@pytest.fixture()
def engine(mock_magika, whitelist):
    return WhitelistMagika(mock_magika, whitelist)


# ---------------------------------------------------------------------------
# Whitelist unit tests
# ---------------------------------------------------------------------------

def test_whitelist_empty_raises():
    with pytest.raises(WhitelistError):
        Whitelist.from_labels([])


def test_whitelist_allows_known_label(whitelist):
    assert whitelist.allows("pdf") is True


def test_whitelist_rejects_unknown_label(whitelist):
    assert whitelist.allows("elf") is False


def test_whitelist_normalises_case():
    wl = Whitelist.from_labels(["PDF", "Python"])
    assert wl.allows("pdf") is True
    assert wl.allows("python") is True


def test_whitelist_len(whitelist):
    assert len(whitelist) == 3


def test_whitelist_repr_contains_labels(whitelist):
    r = repr(whitelist)
    assert "pdf" in r
    assert "Whitelist" in r


# ---------------------------------------------------------------------------
# WhitelistMagika unit tests
# ---------------------------------------------------------------------------

def test_whitelist_property(engine, whitelist):
    assert engine.whitelist is whitelist


def test_identify_bytes_allowed(engine, mock_magika):
    mock_magika.identify_bytes.return_value = _mock_result("pdf")
    result = engine.identify_bytes(b"%PDF-1.4")
    assert result is not None
    assert result.prediction.label == "pdf"


def test_identify_bytes_blocked(engine, mock_magika):
    mock_magika.identify_bytes.return_value = _mock_result("elf")
    result = engine.identify_bytes(b"\x7fELF")
    assert result is None


def test_identify_path_allowed(engine, mock_magika):
    mock_magika.identify_path.return_value = _mock_result("python")
    result = engine.identify_path(Path("script.py"))
    assert result is not None


def test_identify_path_blocked(engine, mock_magika):
    mock_magika.identify_path.return_value = _mock_result("html")
    result = engine.identify_path(Path("page.html"))
    assert result is None


def test_identify_paths_mixed(engine, mock_magika):
    mock_magika.identify_paths.return_value = [
        _mock_result("pdf"),
        _mock_result("elf"),
        _mock_result("zip"),
    ]
    results = engine.identify_paths([Path("a"), Path("b"), Path("c")])
    assert results[0] is not None
    assert results[1] is None
    assert results[2] is not None
