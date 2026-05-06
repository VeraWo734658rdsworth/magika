"""Tests for python/magika/truncate.py"""

from __future__ import annotations

import pytest

from magika.truncate import (
    DEFAULT_HEAD_SIZE,
    DEFAULT_TAIL_SIZE,
    TruncatedContent,
    truncate_bytes,
    truncate_path,
)


# ---------------------------------------------------------------------------
# TruncatedContent helpers
# ---------------------------------------------------------------------------

def test_is_empty_true():
    tc = TruncatedContent(head=b"", tail=b"", total_size=0)
    assert tc.is_empty


def test_is_empty_false():
    tc = TruncatedContent(head=b"abc", tail=b"", total_size=3)
    assert not tc.is_empty


def test_fits_in_head_true():
    tc = TruncatedContent(head=b"hello", tail=b"", total_size=5)
    assert tc.fits_in_head


def test_fits_in_head_false():
    tc = TruncatedContent(head=b"hello", tail=b"world", total_size=1000)
    assert not tc.fits_in_head


# ---------------------------------------------------------------------------
# truncate_bytes
# ---------------------------------------------------------------------------

def test_truncate_bytes_empty():
    tc = truncate_bytes(b"")
    assert tc.is_empty
    assert tc.head == b""
    assert tc.tail == b""


def test_truncate_bytes_small_fits_in_head():
    data = b"tiny"
    tc = truncate_bytes(data, head_size=16, tail_size=16)
    assert tc.head == data
    assert tc.total_size == len(data)
    assert tc.fits_in_head


def test_truncate_bytes_head_and_tail_distinct():
    data = bytes(range(256))
    tc = truncate_bytes(data, head_size=10, tail_size=10)
    assert tc.head == data[:10]
    assert tc.tail == data[-10:]
    assert tc.total_size == 256


def test_truncate_bytes_zero_tail():
    data = b"abcdef"
    tc = truncate_bytes(data, head_size=4, tail_size=0)
    assert tc.tail == b""
    assert tc.head == b"abcd"


def test_truncate_bytes_negative_raises():
    with pytest.raises(ValueError):
        truncate_bytes(b"data", head_size=-1)
    with pytest.raises(ValueError):
        truncate_bytes(b"data", tail_size=-1)


def test_truncate_bytes_defaults():
    data = bytes(2000)
    tc = truncate_bytes(data)
    assert len(tc.head) == DEFAULT_HEAD_SIZE
    assert len(tc.tail) == DEFAULT_TAIL_SIZE


# ---------------------------------------------------------------------------
# truncate_path
# ---------------------------------------------------------------------------

def test_truncate_path_matches_bytes(tmp_path):
    data = bytes(range(256)) * 4  # 1024 bytes
    p = tmp_path / "sample.bin"
    p.write_bytes(data)

    tc_bytes = truncate_bytes(data, head_size=64, tail_size=64)
    tc_path = truncate_path(p, head_size=64, tail_size=64)

    assert tc_path.head == tc_bytes.head
    assert tc_path.tail == tc_bytes.tail
    assert tc_path.total_size == tc_bytes.total_size


def test_truncate_path_small_file(tmp_path):
    data = b"small"
    p = tmp_path / "small.txt"
    p.write_bytes(data)

    tc = truncate_path(p, head_size=512, tail_size=512)
    assert tc.total_size == len(data)
    assert tc.head == data


def test_truncate_path_negative_raises(tmp_path):
    p = tmp_path / "f.bin"
    p.write_bytes(b"x")
    with pytest.raises(ValueError):
        truncate_path(p, head_size=-1)
