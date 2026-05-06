"""Tests for the rule-based override engine."""

from pathlib import Path

import pytest

from magika.rules import DEFAULT_RULES, Rule, RuleEngine


# ---------------------------------------------------------------------------
# Rule unit tests
# ---------------------------------------------------------------------------

class TestRule:
    def test_magic_bytes_match(self):
        rule = Rule(label="pdf", description="PDF", magic_bytes=b"%PDF-")
        assert rule.matches_bytes(b"%PDF-1.4 ...")

    def test_magic_bytes_no_match(self):
        rule = Rule(label="pdf", description="PDF", magic_bytes=b"%PDF-")
        assert not rule.matches_bytes(b"not a pdf")

    def test_extension_match_case_insensitive(self):
        rule = Rule(label="python", description="py", extension=".py")
        assert rule.matches_path(Path("script.PY"))
        assert rule.matches_path(Path("script.py"))

    def test_extension_no_match(self):
        rule = Rule(label="python", description="py", extension=".py")
        assert not rule.matches_path(Path("script.rb"))

    def test_filename_pattern_match(self):
        rule = Rule(label="dockerfile", description="df", filename_pattern=r"^Dockerfile")
        assert rule.matches_path(Path("/project/Dockerfile"))
        assert rule.matches_path(Path("/project/Dockerfile.dev"))

    def test_filename_pattern_no_match(self):
        rule = Rule(label="dockerfile", description="df", filename_pattern=r"^Dockerfile$")
        assert not rule.matches_path(Path("mydockerfile"))


# ---------------------------------------------------------------------------
# RuleEngine tests
# ---------------------------------------------------------------------------

class TestRuleEngine:
    def test_default_rules_loaded(self):
        engine = RuleEngine()
        assert len(engine.rules) == len(DEFAULT_RULES)

    def test_match_pdf_magic(self):
        engine = RuleEngine()
        assert engine.match(b"%PDF-1.7\n") == "pdf"

    def test_match_zip_magic(self):
        engine = RuleEngine()
        assert engine.match(b"PK\x03\x04") == "zip"

    def test_match_python_shebang(self):
        engine = RuleEngine()
        assert engine.match(b"#!/usr/bin/env python\nprint('hi')") == "python"

    def test_match_dockerfile_by_path(self):
        engine = RuleEngine()
        assert engine.match(b"FROM ubuntu:22.04", Path("/repo/Dockerfile")) == "dockerfile"

    def test_match_makefile_by_name(self):
        engine = RuleEngine()
        assert engine.match(b"all:\n\techo done", Path("/repo/Makefile")) == "makefile"

    def test_no_match_returns_none(self):
        engine = RuleEngine()
        assert engine.match(b"random content") is None

    def test_custom_rule_has_higher_priority(self):
        engine = RuleEngine()
        custom = Rule(label="custom", description="custom", magic_bytes=b"%PDF-")
        engine.add_rule(custom)
        assert engine.match(b"%PDF-1.4") == "custom"

    def test_empty_rules(self):
        engine = RuleEngine(rules=[])
        assert engine.match(b"%PDF-1.4") is None

    def test_bytes_takes_priority_over_path(self):
        """Magic-byte rule fires before path rule for same engine scan."""
        engine = RuleEngine()
        # ZIP magic + .py extension — ZIP rule should win (comes first in DEFAULT_RULES)
        result = engine.match(b"PK\x03\x04extra", Path("archive.py"))
        assert result == "zip"
