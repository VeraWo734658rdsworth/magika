"""Label mapping/remapping utilities for Magika.

Allows users to define a mapping from one set of labels to another,
enabling renaming, grouping, or aliasing of content-type labels in
prediction results.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


class LabelMapError(ValueError):
    """Raised when a label map configuration is invalid."""


@dataclass
class LabelMap:
    """A mapping from source labels to target labels."""

    _mapping: Dict[str, str] = field(default_factory=dict)

    def add(self, source: str, target: str) -> None:
        """Register a mapping from *source* label to *target* label."""
        source = source.strip()
        target = target.strip()
        if not source:
            raise LabelMapError("source label must not be empty")
        if not target:
            raise LabelMapError("target label must not be empty")
        self._mapping[source] = target

    def resolve(self, label: str) -> str:
        """Return the mapped label, or the original if no mapping exists."""
        return self._mapping.get(label, label)

    def has_mapping(self, label: str) -> bool:
        """Return True if *label* has an explicit mapping."""
        return label in self._mapping

    def all_sources(self) -> list[str]:
        """Return all registered source labels."""
        return list(self._mapping.keys())

    def all_targets(self) -> list[str]:
        """Return all registered target labels (may contain duplicates)."""
        return list(self._mapping.values())

    @classmethod
    def from_dict(cls, mapping: Dict[str, str]) -> "LabelMap":
        """Construct a LabelMap from a plain dictionary."""
        lm = cls()
        for src, tgt in mapping.items():
            lm.add(src, tgt)
        return lm

    def __len__(self) -> int:
        return len(self._mapping)

    def __repr__(self) -> str:
        return f"LabelMap({self._mapping!r})"
