"""TagMagika — wraps a Magika-compatible object and attaches a TagSet to every result."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from magika.prediction import MagikaResult
from magika.tag import Tag, TagSet


class TagMagika:
    """Decorator that annotates each MagikaResult with user-defined tags.

    Tags are stored in a parallel :class:`TagSet` returned alongside the
    original result.  The inner *magika* object must expose the same
    ``identify_bytes`` / ``identify_path`` / ``identify_paths`` interface as
    :class:`~magika.magika.Magika`.
    """

    def __init__(self, magika: object, tags: Iterable[str | Tag] = ()) -> None:
        self._magika = magika
        self._default_tags: list[Tag] = [
            Tag(t) if isinstance(t, str) else t for t in tags
        ]

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def _make_tag_set(self) -> TagSet:
        ts = TagSet()
        for t in self._default_tags:
            ts.add(t)
        return ts

    def _annotate(self, result: MagikaResult) -> tuple[MagikaResult, TagSet]:
        return result, self._make_tag_set()

    # ------------------------------------------------------------------
    # Identify methods
    # ------------------------------------------------------------------

    def identify_bytes(
        self, content: bytes
    ) -> tuple[MagikaResult, TagSet]:
        result: MagikaResult = self._magika.identify_bytes(content)  # type: ignore[attr-defined]
        return self._annotate(result)

    def identify_path(
        self, path: Path
    ) -> tuple[MagikaResult, TagSet]:
        result: MagikaResult = self._magika.identify_path(path)  # type: ignore[attr-defined]
        return self._annotate(result)

    def identify_paths(
        self, paths: Iterable[Path]
    ) -> list[tuple[MagikaResult, TagSet]]:
        results: List[MagikaResult] = self._magika.identify_paths(list(paths))  # type: ignore[attr-defined]
        return [self._annotate(r) for r in results]
