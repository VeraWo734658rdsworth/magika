"""A Magika wrapper that remaps prediction labels via a LabelMap."""
from __future__ import annotations

from pathlib import Path
from typing import List

from magika.label_map import LabelMap
from magika.magika import Magika
from magika.prediction import MagikaResult


class LabelMapMagika:
    """Wraps a Magika instance and applies a LabelMap to every result.

    The underlying model label is preserved in *prediction.output.ct_label*;
    the remapped label is written to *prediction.output.label* so that
    downstream consumers see the user-defined label instead.
    """

    def __init__(self, inner: Magika, label_map: LabelMap) -> None:
        self._inner = inner
        self._label_map = label_map

    @property
    def label_map(self) -> LabelMap:
        return self._label_map

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _remap(self, result: MagikaResult) -> MagikaResult:
        original = result.prediction.output.ct_label
        remapped = self._label_map.resolve(original)
        if remapped == original:
            return result
        # Shallow-copy the result with the remapped label.
        result.prediction.output.ct_label = remapped
        return result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def identify_bytes(self, content: bytes) -> MagikaResult:
        return self._remap(self._inner.identify_bytes(content))

    def identify_path(self, path: Path) -> MagikaResult:
        return self._remap(self._inner.identify_path(path))

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        return [self._remap(r) for r in self._inner.identify_paths(paths)]
