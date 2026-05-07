"""Normalization utilities for Magika prediction labels and MIME types."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


# Characters considered safe in a normalized label
_LABEL_RE = re.compile(r"^[a-z0-9][a-z0-9_+\-\.]*$")


class NormalizationError(ValueError):
    """Raised when a value cannot be normalized."""


@dataclass(frozen=True)
class NormalizedLabel:
    """A validated, lower-cased content-type label."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise NormalizationError("Label must not be empty.")
        if not _LABEL_RE.match(self.value):
            raise NormalizationError(
                f"Label {self.value!r} contains invalid characters. "
                "Expected lower-case alphanumeric with '_', '+', '-', or '.'."
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class NormalizedMime:
    """A validated, lower-cased MIME type."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise NormalizationError("MIME type must not be empty.")
        parts = self.value.split("/")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise NormalizationError(
                f"MIME type {self.value!r} must have exactly one '/' separating "
                "non-empty type and subtype."
            )

    def __str__(self) -> str:
        return self.value

    @property
    def media_type(self) -> str:
        return self.value.split("/")[0]

    @property
    def subtype(self) -> str:
        return self.value.split("/")[1]


def normalize_label(raw: str) -> NormalizedLabel:
    """Strip whitespace, lower-case, and validate *raw* as a content-type label."""
    cleaned = raw.strip().lower()
    return NormalizedLabel(cleaned)


def normalize_mime(raw: str) -> NormalizedMime:
    """Strip whitespace, lower-case, and validate *raw* as a MIME type."""
    cleaned = raw.strip().lower()
    return NormalizedMime(cleaned)


def try_normalize_label(raw: str) -> Optional[NormalizedLabel]:
    """Return a :class:`NormalizedLabel` or *None* if *raw* is invalid."""
    try:
        return normalize_label(raw)
    except NormalizationError:
        return None


def try_normalize_mime(raw: str) -> Optional[NormalizedMime]:
    """Return a :class:`NormalizedMime` or *None* if *raw* is invalid."""
    try:
        return normalize_mime(raw)
    except NormalizationError:
        return None
