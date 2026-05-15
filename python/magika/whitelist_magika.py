"""A Magika wrapper that filters results to a whitelist of approved labels."""

from __future__ import annotations

from pathlib import Path
from typing import List

from magika.prediction import MagikaResult
from magika.whitelist import Whitelist


class WhitelistMagika:
    """Wraps a Magika-compatible engine and suppresses results not in the whitelist.

    Results whose label is not whitelisted are replaced with a ``None`` entry
    so that callers can detect the suppression without raising an exception.
    """

    def __init__(self, inner, whitelist: Whitelist) -> None:
        self._inner = inner
        self._whitelist = whitelist

    @property
    def whitelist(self) -> Whitelist:
        return self._whitelist

    def _filter(self, result: MagikaResult) -> MagikaResult | None:
        label = result.prediction.label
        if self._whitelist.allows(label):
            return result
        return None

    def identify_bytes(self, content: bytes) -> MagikaResult | None:
        return self._filter(self._inner.identify_bytes(content))

    def identify_path(self, path: Path) -> MagikaResult | None:
        return self._filter(self._inner.identify_path(path))

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult | None]:
        raw = self._inner.identify_paths(paths)
        return [self._filter(r) for r in raw]
