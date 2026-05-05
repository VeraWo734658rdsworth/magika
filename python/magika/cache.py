"""Simple file-based cache for Magika predictions."""

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PredictionCache:
    """Cache for storing and retrieving Magika predictions keyed by file hash."""

    def __init__(self, cache_dir: Optional[Path] = None):
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "magika"
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"PredictionCache initialized at {self._cache_dir}")

    def _get_file_hash(self, path: Path) -> str:
        """Compute SHA-256 hash of a file's content."""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _cache_path(self, file_hash: str) -> Path:
        return self._cache_dir / f"{file_hash}.json"

    def get(self, path: Path) -> Optional[dict]:
        """Retrieve a cached prediction for the given file path."""
        try:
            file_hash = self._get_file_hash(path)
            cache_file = self._cache_path(file_hash)
            if cache_file.exists():
                with open(cache_file, "r") as f:
                    data = json.load(f)
                logger.debug(f"Cache hit for {path} (hash={file_hash[:8]}...)")
                return data
        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Cache read error for {path}: {e}")
        return None

    def put(self, path: Path, prediction: dict) -> None:
        """Store a prediction in the cache."""
        try:
            file_hash = self._get_file_hash(path)
            cache_file = self._cache_path(file_hash)
            with open(cache_file, "w") as f:
                json.dump(prediction, f)
            logger.debug(f"Cached prediction for {path} (hash={file_hash[:8]}...)")
        except OSError as e:
            logger.warning(f"Cache write error for {path}: {e}")

    def clear(self) -> int:
        """Remove all cached entries. Returns count of removed files."""
        removed = 0
        for cache_file in self._cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                removed += 1
            except OSError as e:
                logger.warning(f"Failed to remove cache file {cache_file}: {e}")
        logger.debug(f"Cache cleared: {removed} entries removed")
        return removed

    def size(self) -> int:
        """Return the number of cached entries."""
        return len(list(self._cache_dir.glob("*.json")))
