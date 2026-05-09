"""Label transformation/aliasing for Magika results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LabelAlias:
    """Maps a source label to a canonical target label."""

    source: str
    target: str

    def __post_init__(self) -> None:
        if not self.source:
            raise ValueError("source label must not be empty")
        if not self.target:
            raise ValueError("target label must not be empty")
        self.source = self.source.strip().lower()
        self.target = self.target.strip().lower()

    def matches(self, label: str) -> bool:
        return label.strip().lower() == self.source

    def __repr__(self) -> str:
        return f"LabelAlias({self.source!r} -> {self.target!r})"


@dataclass
class TransformEngine:
    """Applies a set of label aliases to Magika results."""

    aliases: List[LabelAlias] = field(default_factory=list)

    def add_alias(self, source: str, target: str) -> None:
        """Register a new alias."""
        self.aliases.append(LabelAlias(source=source, target=target))

    def transform_label(self, label: str) -> str:
        """Return the target label if an alias matches, else the original."""
        normalised = label.strip().lower()
        for alias in self.aliases:
            if alias.matches(normalised):
                return alias.target
        return normalised

    def transform_many(self, labels: List[str]) -> List[str]:
        """Apply transform_label to each element of *labels*."""
        return [self.transform_label(lbl) for lbl in labels]

    def alias_map(self) -> Dict[str, str]:
        """Return a plain dict snapshot of all registered aliases."""
        return {a.source: a.target for a in self.aliases}
