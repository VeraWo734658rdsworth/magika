"""Tests for magika.transform and TransformMagika."""
from __future__ import annotations

import pytest

from magika.transform import LabelAlias, TransformEngine


# ---------------------------------------------------------------------------
# LabelAlias
# ---------------------------------------------------------------------------

class TestLabelAlias:
    def test_normalises_source_and_target(self):
        a = LabelAlias(source="  JavaScript ", target="JS")
        assert a.source == "javascript"
        assert a.target == "js"

    def test_matches_case_insensitive(self):
        a = LabelAlias(source="python", target="py")
        assert a.matches("Python")
        assert a.matches("PYTHON")
        assert a.matches("python")

    def test_no_match_different_label(self):
        a = LabelAlias(source="python", target="py")
        assert not a.matches("ruby")

    def test_empty_source_raises(self):
        with pytest.raises(ValueError, match="source"):
            LabelAlias(source="", target="py")

    def test_empty_target_raises(self):
        with pytest.raises(ValueError, match="target"):
            LabelAlias(source="python", target="")

    def test_repr_contains_arrow(self):
        a = LabelAlias(source="javascript", target="js")
        assert "->" in repr(a)


# ---------------------------------------------------------------------------
# TransformEngine
# ---------------------------------------------------------------------------

class TestTransformEngine:
    def test_no_aliases_returns_original(self):
        engine = TransformEngine()
        assert engine.transform_label("python") == "python"

    def test_alias_rewrites_label(self):
        engine = TransformEngine()
        engine.add_alias("javascript", "js")
        assert engine.transform_label("javascript") == "js"

    def test_unmatched_label_unchanged(self):
        engine = TransformEngine()
        engine.add_alias("javascript", "js")
        assert engine.transform_label("python") == "python"

    def test_first_alias_wins(self):
        engine = TransformEngine()
        engine.add_alias("python", "py")
        engine.add_alias("python", "python3")
        assert engine.transform_label("python") == "py"

    def test_transform_many(self):
        engine = TransformEngine()
        engine.add_alias("javascript", "js")
        engine.add_alias("typescript", "ts")
        result = engine.transform_many(["javascript", "typescript", "python"])
        assert result == ["js", "ts", "python"]

    def test_alias_map_reflects_registrations(self):
        engine = TransformEngine()
        engine.add_alias("javascript", "js")
        engine.add_alias("typescript", "ts")
        m = engine.alias_map()
        assert m == {"javascript": "js", "typescript": "ts"}

    def test_transform_label_strips_whitespace(self):
        engine = TransformEngine()
        engine.add_alias("python", "py")
        assert engine.transform_label("  python  ") == "py"
