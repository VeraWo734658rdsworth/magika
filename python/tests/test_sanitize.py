"""Tests for python/magika/sanitize.py."""

from __future__ import annotations

import pytest
from pathlib import Path

from magika.sanitize import (
    SanitizationError,
    SanitizedPath,
    sanitize_path,
    sanitize_paths,
    normalize_extension,
)


# ---------------------------------------------------------------------------
# sanitize_path
# ---------------------------------------------------------------------------

def test_sanitize_path_returns_sanitized_path(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("hello")
    result = sanitize_path(f)
    assert isinstance(result, SanitizedPath)
    assert result.path == f.resolve()


def test_sanitize_path_accepts_string(tmp_path):
    f = tmp_path / "file.bin"
    f.write_bytes(b"\x00\x01")
    result = sanitize_path(str(f))
    assert result.path == f.resolve()


def test_sanitize_path_empty_string_raises():
    with pytest.raises(SanitizationError, match="empty"):
        sanitize_path("")


def test_sanitize_path_whitespace_only_raises():
    with pytest.raises(SanitizationError, match="empty"):
        sanitize_path("   ")


def test_sanitize_path_null_byte_raises():
    with pytest.raises(SanitizationError, match="null bytes"):
        sanitize_path("some\x00path")


def test_sanitized_path_equality(tmp_path):
    f = tmp_path / "eq.txt"
    f.write_text("x")
    a = sanitize_path(f)
    b = sanitize_path(f)
    assert a == b


def test_sanitized_path_inequality(tmp_path):
    a_file = tmp_path / "a.txt"
    b_file = tmp_path / "b.txt"
    a_file.write_text("a")
    b_file.write_text("b")
    assert sanitize_path(a_file) != sanitize_path(b_file)


# ---------------------------------------------------------------------------
# sanitize_paths
# ---------------------------------------------------------------------------

def test_sanitize_paths_all_valid(tmp_path):
    files = [tmp_path / f"f{i}.txt" for i in range(3)]
    for f in files:
        f.write_text("data")
    valid, errors = sanitize_paths(files)
    assert len(valid) == 3
    assert errors == []


def test_sanitize_paths_mixed_valid_and_invalid(tmp_path):
    good = tmp_path / "good.txt"
    good.write_text("ok")
    valid, errors = sanitize_paths([good, "", "bad\x00"])
    assert len(valid) == 1
    assert len(errors) == 2


def test_sanitize_paths_empty_list():
    valid, errors = sanitize_paths([])
    assert valid == []
    assert errors == []


# ---------------------------------------------------------------------------
# normalize_extension
# ---------------------------------------------------------------------------

def test_normalize_extension_lowercase():
    assert normalize_extension("Document.PDF") == "pdf"


def test_normalize_extension_no_extension():
    assert normalize_extension("Makefile") == ""


def test_normalize_extension_dotfile():
    assert normalize_extension(".gitignore") == "gitignore"


def test_normalize_extension_path_object():
    assert normalize_extension(Path("/tmp/archive.TAR.GZ")) == "gz"
