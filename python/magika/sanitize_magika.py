"""A Magika wrapper that sanitizes input paths before delegating to an inner engine."""

from __future__ import annotations

from pathlib import Path
from typing import List

from magika.magika import Magika
from magika.prediction import MagikaResult
from magika.sanitize import SanitizationError, sanitize_paths


class SanitizeMagika:
    """Wraps a :class:`Magika` instance and sanitizes paths before identification.

    Invalid paths (empty strings, null bytes, etc.) are silently dropped from
    the result list.  Use :py:attr:`last_errors` to inspect any paths that were
    rejected during the most recent call.
    """

    def __init__(self, magika: Magika | None = None) -> None:
        self._magika = magika if magika is not None else Magika()
        self._last_errors: List[tuple] = []

    @property
    def last_errors(self) -> List[tuple]:
        """Errors from the most recent :meth:`identify_paths` call."""
        return list(self._last_errors)

    def identify_path(self, path: str | Path) -> MagikaResult | None:
        """Identify a single path, returning *None* if sanitization fails."""
        try:
            from magika.sanitize import sanitize_path
            sp = sanitize_path(path)
        except SanitizationError:
            return None
        return self._magika.identify_path(sp.path)

    def identify_paths(self, paths: List[str | Path]) -> List[MagikaResult]:
        """Identify multiple paths, skipping any that fail sanitization.

        Rejected paths are stored in :py:attr:`last_errors`.
        """
        valid, errors = sanitize_paths(paths)
        self._last_errors = errors
        if not valid:
            return []
        return self._magika.identify_paths([sp.path for sp in valid])

    def identify_bytes(self, content: bytes) -> MagikaResult:
        """Identify raw bytes (no sanitization needed; delegates directly)."""
        return self._magika.identify_bytes(content)
