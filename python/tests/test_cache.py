"""Tests for the PredictionCache module."""

import json
import tempfile
from pathlib import Path

import pytest

from magika.cache import PredictionCache


@pytest.fixture
def tmp_cache(tmp_path):
    return PredictionCache(cache_dir=tmp_path / "cache")


@pytest.fixture
def sample_file(tmp_path):
    f = tmp_path / "sample.bin"
    f.write_bytes(b"Hello, Magika! This is test content.")
    return f


def test_cache_miss_on_empty(tmp_cache, sample_file):
    result = tmp_cache.get(sample_file)
    assert result is None


def test_put_and_get(tmp_cache, sample_file):
    prediction = {"label": "text", "score": 0.99}
    tmp_cache.put(sample_file, prediction)
    result = tmp_cache.get(sample_file)
    assert result == prediction


def test_cache_size_increments(tmp_cache, tmp_path):
    assert tmp_cache.size() == 0
    for i in range(3):
        f = tmp_path / f"file_{i}.bin"
        f.write_bytes(f"content {i}".encode())
        tmp_cache.put(f, {"label": f"type_{i}"})
    assert tmp_cache.size() == 3


def test_clear_removes_all_entries(tmp_cache, tmp_path):
    for i in range(4):
        f = tmp_path / f"file_{i}.bin"
        f.write_bytes(f"data {i}".encode())
        tmp_cache.put(f, {"label": "text"})
    removed = tmp_cache.clear()
    assert removed == 4
    assert tmp_cache.size() == 0


def test_different_content_different_cache_entry(tmp_cache, tmp_path):
    f1 = tmp_path / "a.bin"
    f2 = tmp_path / "b.bin"
    f1.write_bytes(b"content A")
    f2.write_bytes(b"content B")
    tmp_cache.put(f1, {"label": "typeA"})
    tmp_cache.put(f2, {"label": "typeB"})
    assert tmp_cache.size() == 2
    assert tmp_cache.get(f1) == {"label": "typeA"}
    assert tmp_cache.get(f2) == {"label": "typeB"}


def test_same_content_same_cache_entry(tmp_cache, tmp_path):
    f1 = tmp_path / "a.bin"
    f2 = tmp_path / "b.bin"
    f1.write_bytes(b"identical content")
    f2.write_bytes(b"identical content")
    tmp_cache.put(f1, {"label": "text"})
    # f2 has same content hash, should hit the same cache entry
    assert tmp_cache.size() == 1
    assert tmp_cache.get(f2) == {"label": "text"}


def test_cache_dir_created_automatically(tmp_path):
    deep_dir = tmp_path / "a" / "b" / "c"
    cache = PredictionCache(cache_dir=deep_dir)
    assert deep_dir.exists()
