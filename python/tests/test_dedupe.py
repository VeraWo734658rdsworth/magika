"""Tests for magika.dedupe and magika.dedupe_magika."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magika.dedupe import count_duplicates, deduplicate
from magika.dedupe_magika import DedupeMagika


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(label: str = "python") -> MagicMock:
    r = MagicMock()
    r.prediction.label = label
    return r


def _pairs(tmp_path: Path, contents: list[bytes]) -> list[tuple[Path, MagicMock]]:
    pairs = []
    for idx, data in enumerate(contents):
        p = tmp_path / f"file_{idx}.bin"
        p.write_bytes(data)
        pairs.append((p, _make_result()))
    return pairs


# ---------------------------------------------------------------------------
# deduplicate()
# ---------------------------------------------------------------------------

def test_deduplicate_all_unique(tmp_path: Path) -> None:
    pairs = _pairs(tmp_path, [b"aaa", b"bbb", b"ccc"])
    result = list(deduplicate(pairs))
    assert len(result) == 3


def test_deduplicate_removes_identical_content(tmp_path: Path) -> None:
    pairs = _pairs(tmp_path, [b"same", b"same", b"different"])
    result = list(deduplicate(pairs))
    assert len(result) == 2


def test_deduplicate_by_path_keeps_all_different_paths(tmp_path: Path) -> None:
    pairs = _pairs(tmp_path, [b"same", b"same"])
    result = list(deduplicate(pairs, by="path"))
    # Different paths even with same content → both kept.
    assert len(result) == 2


def test_deduplicate_by_path_removes_same_path(tmp_path: Path) -> None:
    p = tmp_path / "a.bin"
    p.write_bytes(b"data")
    r = _make_result()
    result = list(deduplicate([(p, r), (p, r)], by="path"))
    assert len(result) == 1


def test_deduplicate_invalid_by_raises() -> None:
    with pytest.raises(ValueError, match="Unknown"):
        list(deduplicate([], by="size"))


# ---------------------------------------------------------------------------
# count_duplicates()
# ---------------------------------------------------------------------------

def test_count_duplicates_none(tmp_path: Path) -> None:
    pairs = _pairs(tmp_path, [b"x", b"y", b"z"])
    assert count_duplicates(pairs) == 0


def test_count_duplicates_two_copies(tmp_path: Path) -> None:
    pairs = _pairs(tmp_path, [b"dup", b"dup", b"dup"])
    assert count_duplicates(pairs) == 2


# ---------------------------------------------------------------------------
# DedupeMagika
# ---------------------------------------------------------------------------

def test_dedupe_magika_calls_model_once_for_identical_files(tmp_path: Path) -> None:
    p1 = tmp_path / "a.bin"
    p2 = tmp_path / "b.bin"
    p1.write_bytes(b"identical")
    p2.write_bytes(b"identical")

    mock_magika = MagicMock()
    mock_magika.identify_paths.return_value = [_make_result()]

    dm = DedupeMagika(mock_magika)
    results = dm.identify_paths([p1, p2])

    assert len(results) == 2
    # Only one novel path → identify_paths called with a list of length 1.
    called_paths = mock_magika.identify_paths.call_args[0][0]
    assert len(called_paths) == 1
    assert dm.cache_hits == 1


def test_dedupe_magika_invalid_by_raises() -> None:
    with pytest.raises(ValueError):
        DedupeMagika(MagicMock(), by="inode")


def test_dedupe_magika_identify_bytes_always_delegates(tmp_path: Path) -> None:
    mock_magika = MagicMock()
    mock_magika.identify_bytes.return_value = _make_result()
    dm = DedupeMagika(mock_magika)
    dm.identify_bytes(b"data")
    mock_magika.identify_bytes.assert_called_once_with(b"data")
