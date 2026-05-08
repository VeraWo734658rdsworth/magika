"""A Magika wrapper that transparently deduplicates results.

Identical files (by content hash) are identified only once; subsequent
occurrences reuse the cached result without re-running inference.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from magika.dedupe import _file_hash
from magika.magika import Magika
from magika.prediction import MagikaResult


class DedupeMagika:
    """Wraps :class:`~magika.magika.Magika` and skips inference for duplicate files.

    Parameters
    ----------
    magika:
        Underlying :class:`Magika` instance used for inference.
    by:
        Deduplication strategy: ``"hash"`` (default) or ``"path"``.
    """

    def __init__(self, magika: Magika, *, by: str = "hash") -> None:
        if by not in ("hash", "path"):
            raise ValueError(f"Unknown deduplication key: {by!r}.")
        self._magika = magika
        self._by = by
        self._cache: dict[str, MagikaResult] = {}
        self._hits: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def cache_hits(self) -> int:
        """Number of times a cached result was reused."""
        return self._hits

    def identify_path(self, path: Path) -> MagikaResult:
        key = self._key(path)
        if key in self._cache:
            self._hits += 1
            return self._cache[key]
        result = self._magika.identify_path(path)
        self._cache[key] = result
        return result

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        results: List[MagikaResult] = []
        unique_keys: list[str] = [self._key(p) for p in paths]

        # Collect paths whose key is not yet cached.
        novel_indices = [i for i, k in enumerate(unique_keys) if k not in self._cache]
        novel_paths = [paths[i] for i in novel_indices]

        if novel_paths:
            novel_results = self._magika.identify_paths(novel_paths)
            for i, result in zip(novel_indices, novel_results):
                self._cache[unique_keys[i]] = result

        for i, key in enumerate(unique_keys):
            if i not in novel_indices:
                self._hits += 1
            results.append(self._cache[key])

        return results

    def identify_bytes(self, data: bytes) -> MagikaResult:
        """Bytes-based identification is always forwarded (no path key available)."""
        return self._magika.identify_bytes(data)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _key(self, path: Path) -> str:
        if self._by == "hash":
            return _file_hash(path)
        return str(path.resolve())
