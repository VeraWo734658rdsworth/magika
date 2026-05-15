"""BlacklistMagika: wraps a MagikaLike and suppresses blacklisted results."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from magika.blacklist import Blacklist
from magika.pipeline import MagikaLike
from magika.prediction import MagikaResult


class BlacklistMagika:
    """Delegates identification to *inner* and returns None for blocked results."""

    def __init__(self, inner: MagikaLike, blacklist: Blacklist) -> None:
        self._inner = inner
        self._blacklist = blacklist

    @property
    def blacklist(self) -> Blacklist:
        return self._blacklist

    def _filter(self, result: MagikaResult) -> Optional[MagikaResult]:
        if self._blacklist.blocks(result):
            return None
        return result

    def identify_bytes(self, content: bytes) -> Optional[MagikaResult]:
        return self._filter(self._inner.identify_bytes(content))

    def identify_path(self, path: Path) -> Optional[MagikaResult]:
        return self._filter(self._inner.identify_path(path))

    def identify_paths(
        self, paths: Sequence[Path]
    ) -> List[Tuple[Path, Optional[MagikaResult]]]:
        out: List[Tuple[Path, Optional[MagikaResult]]] = []
        for path, result in self._inner.identify_paths(paths):
            out.append((path, self._filter(result)))
        return out
