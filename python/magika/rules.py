"""Rule-based override system for Magika predictions.

Allows defining deterministic rules that take precedence over model predictions
for specific file signatures or path patterns.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional


@dataclass
class Rule:
    """A single override rule mapping a condition to a content-type label."""

    label: str
    description: str
    # At least one matcher must be provided
    magic_bytes: Optional[bytes] = None  # prefix match
    extension: Optional[str] = None      # case-insensitive extension
    filename_pattern: Optional[str] = None  # regex on the filename

    def matches_bytes(self, data: bytes) -> bool:
        if self.magic_bytes and data[: len(self.magic_bytes)] == self.magic_bytes:
            return True
        return False

    def matches_path(self, path: Path) -> bool:
        name = path.name
        if self.extension and name.lower().endswith(self.extension.lower()):
            return True
        if self.filename_pattern and re.search(self.filename_pattern, name):
            return True
        return False


# Built-in rules ordered by priority (first match wins)
DEFAULT_RULES: List[Rule] = [
    Rule(
        label="python",
        description="Python shebang",
        magic_bytes=b"#!/usr/bin/env python",
    ),
    Rule(
        label="shell",
        description="Shell shebang",
        magic_bytes=b"#!/bin/sh",
    ),
    Rule(
        label="shell",
        description="Bash shebang",
        magic_bytes=b"#!/bin/bash",
    ),
    Rule(
        label="zip",
        description="ZIP magic bytes",
        magic_bytes=b"PK\x03\x04",
    ),
    Rule(
        label="pdf",
        description="PDF magic bytes",
        magic_bytes=b"%PDF-",
    ),
    Rule(
        label="dockerfile",
        description="Dockerfile by name",
        filename_pattern=r"^Dockerfile(\..*)?$",
    ),
    Rule(
        label="makefile",
        description="Makefile by name",
        filename_pattern=r"^[Mm]akefile$",
    ),
]


class RuleEngine:
    """Evaluates a list of rules against bytes and/or a path."""

    def __init__(self, rules: Optional[List[Rule]] = None) -> None:
        self._rules: List[Rule] = rules if rules is not None else list(DEFAULT_RULES)

    @property
    def rules(self) -> List[Rule]:
        return list(self._rules)

    def add_rule(self, rule: Rule) -> None:
        self._rules.insert(0, rule)  # higher priority than defaults

    def match(self, data: bytes, path: Optional[Path] = None) -> Optional[str]:
        """Return the label of the first matching rule, or None."""
        for rule in self._rules:
            if rule.matches_bytes(data):
                return rule.label
            if path is not None and rule.matches_path(path):
                return rule.label
        return None
