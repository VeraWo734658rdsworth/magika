"""Deduplication support for Magika results.

Provides utilities to deduplicate a sequence of (path, result) pairs
based on file content hash so that identical files are only reported once.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable, Iterator

from magika.prediction import MagikaResult


def _file_hash(path: Path, block_size: int = 65536) -> str:
    """Return the SHA-256 hex digest of *path*."""
    h = hashlib.sha256()
    try:
        with path.open("rb") as fh:
            for block in iter(lambda: fh.read(block_size), b""):
                h.update(block)
    except OSError:
        # Unreadable files get a unique sentinel so they are never deduped.
        return f"unreadable:{path}"
    return h.hexdigest()


def deduplicate(
    pairs: Iterable[tuple[Path, MagikaResult]],
    *,
    by: str = "hash",
) -> Iterator[tuple[Path, MagikaResult]]:
    """Yield each unique (path, result) pair exactly once.

    Parameters
    ----------
    pairs:
        Iterable of ``(path, result)`` tuples as returned by Magika.
    by:
        Deduplication key.  ``"hash"`` (default) compares file content;
        ``"path"`` compares resolved absolute paths.

    Yields
    ------
    The first occurrence of each unique file.
    """
    if by not in ("hash", "path"):
        raise ValueError(f"Unknown deduplication key: {by!r}. Use 'hash' or 'path'.")

    seen: set[str] = set()
    for path, result in pairs:
        if by == "hash":
            key = _file_hash(path)
        else:
            key = str(path.resolve())

        if key not in seen:
            seen.add(key)
            yield path, result


def count_duplicates(
    pairs: Iterable[tuple[Path, MagikaResult]],
    *,
    by: str = "hash",
) -> int:
    """Return the number of duplicate entries that *deduplicate* would drop."""
    if by not in ("hash", "path"):
        raise ValueError(f"Unknown deduplication key: {by!r}. Use 'hash' or 'path'.")

    seen: set[str] = set()
    duplicates = 0
    for path, _result in pairs:
        key = _file_hash(path) if by == "hash" else str(path.resolve())
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
    return duplicates
