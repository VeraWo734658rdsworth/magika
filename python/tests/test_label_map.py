"""Unit tests for python/magika/label_map.py."""
from __future__ import annotations

import pytest

from magika.label_map import LabelMap, LabelMapError


# ---------------------------------------------------------------------------
# LabelMap construction
# ---------------------------------------------------------------------------

def test_empty_map_has_zero_length():
    lm = LabelMap()
    assert len(lm) == 0


def test_add_single_mapping():
    lm = LabelMap()
    lm.add("javascript", "js")
    assert len(lm) == 1


def test_resolve_known_label():
    lm = LabelMap()
    lm.add("javascript", "js")
    assert lm.resolve("javascript") == "js"


def test_resolve_unknown_label_returns_original():
    lm = LabelMap()
    lm.add("javascript", "js")
    assert lm.resolve("python") == "python"


def test_has_mapping_true():
    lm = LabelMap()
    lm.add("pdf", "document")
    assert lm.has_mapping("pdf") is True


def test_has_mapping_false():
    lm = LabelMap()
    assert lm.has_mapping("pdf") is False


def test_add_empty_source_raises():
    lm = LabelMap()
    with pytest.raises(LabelMapError):
        lm.add("", "something")


def test_add_whitespace_only_source_raises():
    lm = LabelMap()
    with pytest.raises(LabelMapError):
        lm.add("   ", "something")


def test_add_empty_target_raises():
    lm = LabelMap()
    with pytest.raises(LabelMapError):
        lm.add("pdf", "")


def test_all_sources():
    lm = LabelMap()
    lm.add("pdf", "document")
    lm.add("docx", "document")
    assert set(lm.all_sources()) == {"pdf", "docx"}


def test_all_targets_may_have_duplicates():
    lm = LabelMap()
    lm.add("pdf", "document")
    lm.add("docx", "document")
    assert lm.all_targets().count("document") == 2


def test_from_dict():
    lm = LabelMap.from_dict({"javascript": "js", "typescript": "ts"})
    assert lm.resolve("javascript") == "js"
    assert lm.resolve("typescript") == "ts"
    assert len(lm) == 2


def test_from_dict_empty():
    lm = LabelMap.from_dict({})
    assert len(lm) == 0


def test_repr_contains_mapping():
    lm = LabelMap()
    lm.add("pdf", "document")
    assert "pdf" in repr(lm)
    assert "document" in repr(lm)


def test_overwrite_existing_mapping():
    lm = LabelMap()
    lm.add("pdf", "document")
    lm.add("pdf", "binary")  # overwrite
    assert lm.resolve("pdf") == "binary"
