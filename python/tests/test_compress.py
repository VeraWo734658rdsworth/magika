"""Tests for python/magika/compress.py."""

from __future__ import annotations

import gzip
import zlib

import pytest

from magika.compress import (
    CompressionPolicy,
    DecompressionError,
    decompress_bytes,
    detect_compression,
)


# ---------------------------------------------------------------------------
# CompressionPolicy
# ---------------------------------------------------------------------------

def test_default_policy_is_valid() -> None:
    p = CompressionPolicy()
    assert p.decompress_gzip is True
    assert p.decompress_zlib is True
    assert p.max_decompressed_bytes > 0


def test_policy_rejects_zero_max() -> None:
    with pytest.raises(ValueError):
        CompressionPolicy(max_decompressed_bytes=0)


def test_policy_rejects_negative_max() -> None:
    with pytest.raises(ValueError):
        CompressionPolicy(max_decompressed_bytes=-1)


# ---------------------------------------------------------------------------
# detect_compression
# ---------------------------------------------------------------------------

def test_detect_gzip() -> None:
    data = gzip.compress(b"hello")
    assert detect_compression(data) == "gzip"


def test_detect_zlib() -> None:
    data = zlib.compress(b"hello")
    result = detect_compression(data)
    assert result == "zlib"


def test_detect_plain_returns_none() -> None:
    assert detect_compression(b"hello world") is None


def test_detect_empty_returns_none() -> None:
    assert detect_compression(b"") is None


# ---------------------------------------------------------------------------
# decompress_bytes
# ---------------------------------------------------------------------------

def test_decompress_gzip_roundtrip() -> None:
    original = b"the quick brown fox"
    compressed = gzip.compress(original)
    policy = CompressionPolicy()
    assert decompress_bytes(compressed, policy) == original


def test_decompress_zlib_roundtrip() -> None:
    original = b"pack my box with five dozen liquor jugs"
    compressed = zlib.compress(original)
    policy = CompressionPolicy()
    assert decompress_bytes(compressed, policy) == original


def test_decompress_plain_returns_unchanged() -> None:
    data = b"plain text"
    policy = CompressionPolicy()
    assert decompress_bytes(data, policy) == data


def test_decompress_gzip_disabled_returns_raw() -> None:
    compressed = gzip.compress(b"hello")
    policy = CompressionPolicy(decompress_gzip=False)
    assert decompress_bytes(compressed, policy) == compressed


def test_decompress_truncates_to_max() -> None:
    original = b"a" * 1000
    compressed = gzip.compress(original)
    policy = CompressionPolicy(max_decompressed_bytes=100)
    result = decompress_bytes(compressed, policy)
    assert len(result) == 100


def test_decompress_invalid_gzip_raises() -> None:
    bad = b"\x1f\x8b" + b"not real gzip data"
    policy = CompressionPolicy()
    with pytest.raises(DecompressionError):
        decompress_bytes(bad, policy)
