"""FilteredMagika — a Magika wrapper that post-filters identification results."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from magika.filter import ResultFilter
from magika.magika import Magika
from magika.prediction import MagikaResult


class FilteredMagika:
    """Wraps :class:`Magika` and discards results that do not pass *result_filter*.

    Paths whose results are filtered out are simply omitted from the returned
    list, so callers should not rely on positional correspondence between input
    paths and output results.
    """

    def __init__(self, result_filter: ResultFilter, magika: Magika | None = None) -> None:
        self._filter = result_filter
        self._magika = magika or Magika()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def identify_path(self, path: Path) -> List[MagikaResult]:
        """Identify *path* and return a list with 0 or 1 results."""
        result = self._magika.identify_path(path)
        return self._filter.apply([result])

    def identify_paths(self, paths: Iterable[Path]) -> List[MagikaResult]:
        """Identify all *paths* and return only those passing the filter."""
        results = self._magika.identify_paths(list(paths))
        return self._filter.apply(results)

    def identify_bytes(self, content: bytes) -> List[MagikaResult]:
        """Identify *content* and return a list with 0 or 1 results."""
        result = self._magika.identify_bytes(content)
        return self._filter.apply([result])

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def active_filter(self) -> ResultFilter:
        """Return the :class:`ResultFilter` in use."""
        return self._filter

    def __repr__(self) -> str:  # pragma: no cover
        return f"FilteredMagika(filter={self._filter!r})"
