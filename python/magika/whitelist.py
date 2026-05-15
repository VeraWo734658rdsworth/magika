"""Whitelist support: only allow results whose labels appear in an approved set."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


class WhitelistError(Exception):
    """Raised when the whitelist is misconfigured."""


@dataclass
class Whitelist:
    """An immutable set of approved content-type labels."""

    _labels: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not self._labels:
            raise WhitelistError("Whitelist must contain at least one label.")
        for label in self._labels:
            if not label or not label.strip():
                raise WhitelistError("Whitelist labels must be non-empty strings.")

    @classmethod
    def from_labels(cls, labels: Iterable[str]) -> "Whitelist":
        normalised = frozenset(lbl.strip().lower() for lbl in labels)
        return cls(_labels=normalised)

    def allows(self, label: str) -> bool:
        """Return True if *label* is in the whitelist."""
        return label.strip().lower() in self._labels

    def labels(self) -> frozenset[str]:
        return self._labels

    def __len__(self) -> int:
        return len(self._labels)

    def __repr__(self) -> str:
        return f"Whitelist(labels={sorted(self._labels)})"
