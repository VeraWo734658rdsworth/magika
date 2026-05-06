"""Magika wrapper that applies user-supplied label overrides before inference."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from magika.magika import Magika
from magika.override import OverrideEngine
from magika.prediction import MagikaResult, PredictionDetails
from magika.content_types import get_content_type
from magika.types import Status


class OverrideMagika:
    """Wraps :class:`Magika` and short-circuits inference when an override matches."""

    def __init__(self, engine: Optional[OverrideEngine] = None, **magika_kwargs) -> None:
        self._magika = Magika(**magika_kwargs)
        self._engine = engine or OverrideEngine()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def identify_path(self, path: Path) -> MagikaResult:
        label = self._engine.resolve_path(path)
        if label is not None:
            return self._make_override_result(label)
        return self._magika.identify_path(path)

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        results: List[MagikaResult] = []
        for path in paths:
            results.append(self.identify_path(path))
        return results

    def identify_bytes(self, data: bytes) -> MagikaResult:
        # No path available — fall through to model directly.
        return self._magika.identify_bytes(data)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_override_result(label: str) -> MagikaResult:
        ct_info = get_content_type(label)
        details = PredictionDetails.from_content_type_info(
            ct_info,
            score=1.0,
            status=Status.OK,
        )
        return MagikaResult(path=Path("-"), status=Status.OK, prediction=details)
