"""Integration-style tests: RuleEngine + real files on disk."""

import textwrap
from pathlib import Path

import pytest

from magika.rules import RuleEngine


@pytest.fixture()
def sample_dir(tmp_path: Path) -> Path:
    # Python script with shebang
    (tmp_path / "run.py").write_bytes(b"#!/usr/bin/env python\nprint('hello')")
    # Bash script
    (tmp_path / "deploy.sh").write_bytes(b"#!/bin/bash\necho deploy")
    # PDF
    (tmp_path / "report.pdf").write_bytes(b"%PDF-1.7\n%%EOF")
    # ZIP (fake)
    (tmp_path / "archive.zip").write_bytes(b"PK\x03\x04" + b"\x00" * 20)
    # Plain text
    (tmp_path / "notes.txt").write_bytes(b"Just some notes.")
    # Dockerfile
    (tmp_path / "Dockerfile").write_bytes(b"FROM python:3.12")
    # Makefile
    (tmp_path / "Makefile").write_bytes(b"all:\n\techo done")
    return tmp_path


class TestRuleEngineWithFiles:
    def _read(self, path: Path, size: int = 512) -> bytes:
        return path.read_bytes()[:size]

    def test_python_script(self, sample_dir):
        engine = RuleEngine()
        p = sample_dir / "run.py"
        assert engine.match(self._read(p), p) == "python"

    def test_shell_script(self, sample_dir):
        engine = RuleEngine()
        p = sample_dir / "deploy.sh"
        assert engine.match(self._read(p), p) == "shell"

    def test_pdf_file(self, sample_dir):
        engine = RuleEngine()
        p = sample_dir / "report.pdf"
        assert engine.match(self._read(p), p) == "pdf"

    def test_zip_file(self, sample_dir):
        engine = RuleEngine()
        p = sample_dir / "archive.zip"
        assert engine.match(self._read(p), p) == "zip"

    def test_plain_text_no_match(self, sample_dir):
        engine = RuleEngine()
        p = sample_dir / "notes.txt"
        assert engine.match(self._read(p), p) is None

    def test_dockerfile(self, sample_dir):
        engine = RuleEngine()
        p = sample_dir / "Dockerfile"
        assert engine.match(self._read(p), p) == "dockerfile"

    def test_makefile(self, sample_dir):
        engine = RuleEngine()
        p = sample_dir / "Makefile"
        assert engine.match(self._read(p), p) == "makefile"

    def test_all_files_scanned(self, sample_dir):
        engine = RuleEngine()
        results = {}
        for p in sorted(sample_dir.iterdir()):
            results[p.name] = engine.match(self._read(p), p)
        assert results["run.py"] == "python"
        assert results["deploy.sh"] == "shell"
        assert results["report.pdf"] == "pdf"
        assert results["archive.zip"] == "zip"
        assert results["notes.txt"] is None
        assert results["Dockerfile"] == "dockerfile"
        assert results["Makefile"] == "makefile"
