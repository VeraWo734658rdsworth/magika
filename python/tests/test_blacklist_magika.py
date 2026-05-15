"""Tests for blacklist.py and blacklist_magika.py."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.blacklist import Blacklist, BlacklistError
from magika.blacklist_magika import BlacklistMagika


def _mock_result(label: str, mime: str):
    result = MagicMock()
    result.dl.ct_label = label
    result.output.mime_type = mime
    return result


# ---------------------------------------------------------------------------
# Blacklist construction
# ---------------------------------------------------------------------------

def test_empty_blacklist_raises():
    with pytest.raises(BlacklistError):
        Blacklist()


def test_from_labels_normalises_case():
    bl = Blacklist.from_labels(["PDF", " Html "])
    assert "pdf" in bl.labels
    assert "html" in bl.labels


def test_from_mime_types_normalises_case():
    bl = Blacklist.from_mime_types(["Application/PDF"])
    assert "application/pdf" in bl.mime_types


def test_empty_label_string_raises():
    with pytest.raises(BlacklistError):
        Blacklist(labels=[""])


def test_empty_mime_string_raises():
    with pytest.raises(BlacklistError):
        Blacklist(mime_types=[""])


# ---------------------------------------------------------------------------
# Blacklist.blocks
# ---------------------------------------------------------------------------

def test_blocks_by_label():
    bl = Blacklist.from_labels(["pdf"])
    result = _mock_result("pdf", "application/pdf")
    assert bl.blocks(result) is True


def test_blocks_by_mime():
    bl = Blacklist.from_mime_types(["application/pdf"])
    result = _mock_result("pdf", "application/pdf")
    assert bl.blocks(result) is True


def test_does_not_block_unrelated():
    bl = Blacklist.from_labels(["pdf"])
    result = _mock_result("python", "text/x-python")
    assert bl.blocks(result) is False


# ---------------------------------------------------------------------------
# BlacklistMagika
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_magika():
    return MagicMock()


@pytest.fixture()
def engine(mock_magika):
    bl = Blacklist.from_labels(["pdf"])
    return BlacklistMagika(mock_magika, bl)


def test_blacklist_property(engine):
    assert isinstance(engine.blacklist, Blacklist)


def test_identify_bytes_returns_none_when_blocked(engine, mock_magika):
    mock_magika.identify_bytes.return_value = _mock_result("pdf", "application/pdf")
    assert engine.identify_bytes(b"%PDF") is None


def test_identify_bytes_passes_through_allowed(engine, mock_magika):
    result = _mock_result("python", "text/x-python")
    mock_magika.identify_bytes.return_value = result
    assert engine.identify_bytes(b"print()") is result


def test_identify_path_returns_none_when_blocked(engine, mock_magika):
    mock_magika.identify_path.return_value = _mock_result("pdf", "application/pdf")
    assert engine.identify_path(Path("file.pdf")) is None


def test_identify_paths_filters_blocked(engine, mock_magika):
    p1, p2 = Path("a.pdf"), Path("b.py")
    mock_magika.identify_paths.return_value = [
        (p1, _mock_result("pdf", "application/pdf")),
        (p2, _mock_result("python", "text/x-python")),
    ]
    results = engine.identify_paths([p1, p2])
    blocked = [r for _, r in results if r is None]
    allowed = [r for _, r in results if r is not None]
    assert len(blocked) == 1
    assert len(allowed) == 1
