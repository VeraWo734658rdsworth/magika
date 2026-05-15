"""Blacklist: reject results whose label or MIME type is explicitly disallowed."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from magika.prediction import MagikaResult


class BlacklistError(ValueError):
    """Raised when a Blacklist is constructed with invalid arguments."""


@dataclass
class Blacklist:
    """An immutable set of disallowed labels and/or MIME types."""

    labels: List[str] = field(default_factory=list)
    mime_types: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.labels and not self.mime_types:
            raise BlacklistError(
                "Blacklist requires at least one label or MIME type."
            )
        self.labels = [lbl.strip().lower() for lbl in self.labels]
        self.mime_types = [m.strip().lower() for m in self.mime_types]
        if any(not lbl for lbl in self.labels):
            raise BlacklistError("Blacklist labels must not be empty strings.")
        if any(not m for m in self.mime_types):
            raise BlacklistError("Blacklist MIME types must not be empty strings.")

    @classmethod
    def from_labels(cls, labels: Iterable[str]) -> "Blacklist":
        return cls(labels=list(labels))

    @classmethod
    def from_mime_types(cls, mime_types: Iterable[str]) -> "Blacklist":
        return cls(mime_types=list(mime_types))

    def blocks(self, result: MagikaResult) -> bool:
        """Return True if *result* should be suppressed by this blacklist."""
        label = (result.dl.ct_label or "").lower()
        mime = (result.output.mime_type or "").lower()
        return label in self.labels or mime in self.mime_types

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Blacklist(labels={self.labels!r}, mime_types={self.mime_types!r})"
        )
