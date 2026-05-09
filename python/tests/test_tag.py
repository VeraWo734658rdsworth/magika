"""Tests for python/magika/tag.py and python/magika/tag_magika.py."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.tag import Tag, TagError, TagSet
from magika.tag_magika import TagMagika


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------

class TestTag:
    def test_valid_tag(self):
        t = Tag("malware")
        assert str(t) == "malware"

    def test_empty_raises(self):
        with pytest.raises(TagError):
            Tag("")

    def test_whitespace_only_raises(self):
        with pytest.raises(TagError):
            Tag("   ")

    def test_leading_whitespace_raises(self):
        with pytest.raises(TagError):
            Tag(" suspicious")

    def test_trailing_whitespace_raises(self):
        with pytest.raises(TagError):
            Tag("suspicious ")

    def test_repr(self):
        assert repr(Tag("x")) == "Tag('x')"

    def test_equality(self):
        assert Tag("a") == Tag("a")

    def test_inequality(self):
        assert Tag("a") != Tag("b")

    def test_hashable(self):
        s = {Tag("a"), Tag("a"), Tag("b")}
        assert len(s) == 2


# ---------------------------------------------------------------------------
# TagSet
# ---------------------------------------------------------------------------

class TestTagSet:
    def test_empty_on_init(self):
        ts = TagSet()
        assert len(ts) == 0

    def test_add_str(self):
        ts = TagSet()
        ts.add("archive")
        assert ts.has("archive")

    def test_add_tag_object(self):
        ts = TagSet()
        ts.add(Tag("pdf"))
        assert ts.has(Tag("pdf"))

    def test_remove_existing(self):
        ts = TagSet()
        ts.add("x")
        ts.remove("x")
        assert not ts.has("x")

    def test_remove_missing_is_silent(self):
        ts = TagSet()
        ts.remove("nope")  # should not raise

    def test_all_returns_frozenset(self):
        ts = TagSet()
        ts.add("a")
        ts.add("b")
        result = ts.all()
        assert isinstance(result, frozenset)
        assert len(result) == 2

    def test_filter_by_prefix(self):
        ts = TagSet()
        for name in ["risk:high", "risk:low", "category:text"]:
            ts.add(name)
        filtered = ts.filter("risk:")
        assert [str(t) for t in filtered] == ["risk:high", "risk:low"]

    def test_iter_sorted(self):
        ts = TagSet()
        for name in ["c", "a", "b"]:
            ts.add(name)
        assert [str(t) for t in ts] == ["a", "b", "c"]

    def test_repr_contains_tags(self):
        ts = TagSet()
        ts.add("hello")
        assert "hello" in repr(ts)


# ---------------------------------------------------------------------------
# TagMagika
# ---------------------------------------------------------------------------

def _mock_result():
    r = MagicMock()
    r.prediction.label = "pdf"
    return r


@pytest.fixture()
def mock_magika():
    m = MagicMock()
    m.identify_bytes.return_value = _mock_result()
    m.identify_path.return_value = _mock_result()
    m.identify_paths.return_value = [_mock_result(), _mock_result()]
    return m


@pytest.fixture()
def engine(mock_magika):
    return TagMagika(mock_magika, tags=["source:test", "env:ci"])


class TestTagMagika:
    def test_identify_bytes_returns_tuple(self, engine):
        result, ts = engine.identify_bytes(b"%PDF")
        assert result is not None
        assert isinstance(ts, TagSet)

    def test_default_tags_present(self, engine):
        _, ts = engine.identify_bytes(b"data")
        assert ts.has("source:test")
        assert ts.has("env:ci")

    def test_identify_path_returns_tuple(self, engine):
        result, ts = engine.identify_path(Path("/tmp/file.pdf"))
        assert isinstance(ts, TagSet)

    def test_identify_paths_returns_list_of_tuples(self, engine):
        pairs = engine.identify_paths([Path("/a"), Path("/b")])
        assert len(pairs) == 2
        for result, ts in pairs:
            assert isinstance(ts, TagSet)
            assert ts.has("source:test")

    def test_no_default_tags_yields_empty_set(self, mock_magika):
        eng = TagMagika(mock_magika)
        _, ts = eng.identify_bytes(b"data")
        assert len(ts) == 0

    def test_tag_sets_are_independent(self, engine):
        _, ts1 = engine.identify_bytes(b"a")
        _, ts2 = engine.identify_bytes(b"b")
        ts1.add("extra")
        assert not ts2.has("extra")
