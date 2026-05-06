"""Tests for magika.override (LabelOverride and OverrideEngine)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from magika.override import LabelOverride, OverrideEngine


# ---------------------------------------------------------------------------
# LabelOverride
# ---------------------------------------------------------------------------

class TestLabelOverride:
    def test_requires_extension_or_mime(self):
        with pytest.raises(ValueError):
            LabelOverride(label="python")

    def test_extension_normalised(self):
        rule = LabelOverride(extension=".PY", label="python")
        assert rule.extension == "py"

    def test_mime_normalised(self):
        rule = LabelOverride(mime="Text/Plain", label="txt")
        assert rule.mime == "text/plain"

    def test_matches_path_true(self):
        rule = LabelOverride(extension="py", label="python")
        assert rule.matches_path(Path("script.py")) is True

    def test_matches_path_case_insensitive(self):
        rule = LabelOverride(extension="py", label="python")
        assert rule.matches_path(Path("script.PY")) is True

    def test_matches_path_false(self):
        rule = LabelOverride(extension="py", label="python")
        assert rule.matches_path(Path("archive.zip")) is False

    def test_matches_path_no_extension_rule(self):
        rule = LabelOverride(mime="text/plain", label="txt")
        assert rule.matches_path(Path("file.txt")) is False

    def test_matches_mime_true(self):
        rule = LabelOverride(mime="text/plain", label="txt")
        assert rule.matches_mime("text/plain") is True

    def test_matches_mime_false(self):
        rule = LabelOverride(mime="text/plain", label="txt")
        assert rule.matches_mime("application/pdf") is False


# ---------------------------------------------------------------------------
# OverrideEngine
# ---------------------------------------------------------------------------

class TestOverrideEngine:
    def test_empty_engine_returns_none_for_path(self):
        engine = OverrideEngine()
        assert engine.resolve_path(Path("file.py")) is None

    def test_empty_engine_returns_none_for_mime(self):
        engine = OverrideEngine()
        assert engine.resolve_mime("text/plain") is None

    def test_resolve_path_matches(self):
        rule = LabelOverride(extension="rs", label="rust")
        engine = OverrideEngine([rule])
        assert engine.resolve_path(Path("main.rs")) == "rust"

    def test_resolve_mime_matches(self):
        rule = LabelOverride(mime="application/pdf", label="pdf")
        engine = OverrideEngine([rule])
        assert engine.resolve_mime("application/pdf") == "pdf"

    def test_first_matching_rule_wins(self):
        rules = [
            LabelOverride(extension="py", label="python"),
            LabelOverride(extension="py", label="text"),
        ]
        engine = OverrideEngine(rules)
        assert engine.resolve_path(Path("a.py")) == "python"

    def test_from_dict(self):
        data = {"overrides": [{"extension": "go", "label": "go"}]}
        engine = OverrideEngine.from_dict(data)
        assert len(engine) == 1
        assert engine.resolve_path(Path("main.go")) == "go"

    def test_from_json_file(self, tmp_path: Path):
        data = {"overrides": [{"mime": "text/x-sh", "label": "shell"}]}
        cfg = tmp_path / "overrides.json"
        cfg.write_text(json.dumps(data))
        engine = OverrideEngine.from_json_file(cfg)
        assert engine.resolve_mime("text/x-sh") == "shell"

    def test_len(self):
        rules = [LabelOverride(extension="c", label="c"), LabelOverride(extension="h", label="c")]
        engine = OverrideEngine(rules)
        assert len(engine) == 2
