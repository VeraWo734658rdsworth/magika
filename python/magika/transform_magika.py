"""Magika wrapper that rewrites result labels via a TransformEngine."""
from __future__ import annotations

from pathlib import Path
from typing import List

from magika.magika import Magika
from magika.prediction import MagikaResult
from magika.transform import TransformEngine


class TransformMagika:
    """Wraps a :class:`Magika` instance and rewrites labels using aliases.

    Example::

        engine = TransformMagika(Magika())
        engine.add_alias("javascript", "js")
        result = engine.identify_bytes(b"console.log('hi')")
        assert result.output.ct_label == "js"
    """

    def __init__(self, inner: Magika, transform: TransformEngine | None = None) -> None:
        self._inner = inner
        self._transform = transform or TransformEngine()

    def add_alias(self, source: str, target: str) -> None:
        """Convenience proxy to :meth:`TransformEngine.add_alias`."""
        self._transform.add_alias(source, target)

    @property
    def transform(self) -> TransformEngine:
        return self._transform

    def _apply(self, result: MagikaResult) -> MagikaResult:
        original = result.output.ct_label
        new_label = self._transform.transform_label(original)
        if new_label == original:
            return result
        # Shallow-copy the result with the rewritten label.
        import copy
        out = copy.deepcopy(result)
        out.output.ct_label = new_label
        return out

    def identify_bytes(self, data: bytes) -> MagikaResult:
        return self._apply(self._inner.identify_bytes(data))

    def identify_path(self, path: Path) -> MagikaResult:
        return self._apply(self._inner.identify_path(path))

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        return [self._apply(r) for r in self._inner.identify_paths(paths)]
