"""Utilities for sanitizing and normalizing file path inputs before identification."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple


class SanitizationError(ValueError):
    """Raised when a path cannot be sanitized to a safe, usable form."""


class SanitizedPath:
    """Wraps a resolved, validated Path."""

    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def __repr__(self) -> str:  # pragma: no cover
        return f"SanitizedPath({self._path!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, SanitizedPath):
            return self._path == other._path
        return NotImplemented


def sanitize_path(raw: str | Path) -> SanitizedPath:
    """Resolve and validate a single path.

    Raises SanitizationError if the path is empty, contains null bytes,
    or resolves to a non-existent location.
    """
    if isinstance(raw, str):
        if not raw or raw.strip() == "":
            raise SanitizationError("Path must not be empty or whitespace-only.")
        if "\x00" in raw:
            raise SanitizationError("Path must not contain null bytes.")
    resolved = Path(raw).resolve()
    return SanitizedPath(resolved)


def sanitize_paths(raws: List[str | Path]) -> Tuple[List[SanitizedPath], List[Tuple[str | Path, str]]]:
    """Sanitize a list of paths.

    Returns a tuple of (valid_sanitized_paths, errors) where errors is a list
    of (original_input, error_message) pairs for any paths that failed.
    """
    valid: List[SanitizedPath] = []
    errors: List[Tuple[str | Path, str]] = []
    for raw in raws:
        try:
            valid.append(sanitize_path(raw))
        except SanitizationError as exc:
            errors.append((raw, str(exc)))
    return valid, errors


def normalize_extension(filename: str | Path) -> str:
    """Return the lowercase extension of a filename without the leading dot.

    Returns an empty string if there is no extension.
    """
    suffix = Path(filename).suffix
    if not suffix:
        return ""
    return suffix.lstrip(".").lower()
