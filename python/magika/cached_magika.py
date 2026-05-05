"""Magika wrapper that adds prediction caching support."""

import logging
from pathlib import Path
from typing import List, Optional

from magika.cache import PredictionCache
from magika.magika import Magika
from magika.prediction import MagikaResult

logger = logging.getLogger(__name__)


class CachedMagika:
    """A Magika wrapper that caches results to avoid redundant inference.

    Predictions are cached on disk keyed by the SHA-256 hash of the file
    content, so results are reused across process restarts as long as the
    file content has not changed.
    """

    def __init__(
        self,
        magika: Optional[Magika] = None,
        cache_dir: Optional[Path] = None,
    ):
        self._magika = magika if magika is not None else Magika()
        self._cache = PredictionCache(cache_dir=cache_dir)

    def identify_path(self, path: Path) -> MagikaResult:
        """Identify the content type of a single file, using cache when available."""
        path = Path(path)
        cached = self._cache.get(path)
        if cached is not None:
            return MagikaResult.from_dict(cached)
        result = self._magika.identify_path(path)
        self._cache.put(path, result.to_dict())
        return result

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        """Identify content types for multiple files, using cache where possible."""
        results: List[MagikaResult] = []
        uncached_paths: List[Path] = []
        uncached_indices: List[int] = []

        for i, path in enumerate(paths):
            path = Path(path)
            cached = self._cache.get(path)
            if cached is not None:
                results.append((i, MagikaResult.from_dict(cached)))
            else:
                uncached_paths.append(path)
                uncached_indices.append(i)
                results.append((i, None))  # placeholder

        if uncached_paths:
            new_results = self._magika.identify_paths(uncached_paths)
            for path, result, idx in zip(uncached_paths, new_results, uncached_indices):
                self._cache.put(path, result.to_dict())
                results[idx] = (idx, result)

        return [r for _, r in sorted(results, key=lambda x: x[0])]

    def clear_cache(self) -> int:
        """Clear all cached predictions. Returns number of removed entries."""
        return self._cache.clear()

    def cache_size(self) -> int:
        """Return the number of entries currently in the cache."""
        return self._cache.size()
