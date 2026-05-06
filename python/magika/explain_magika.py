"""ExplainMagika: wraps Magika and attaches explanations to every result."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from magika.magika import Magika
from magika.prediction import MagikaResult
from magika.explain import PredictionExplanation, explain_result


class ExplainMagika:
    """Thin wrapper around Magika that also returns PredictionExplanation objects."""

    def __init__(self, magika: Magika | None = None) -> None:
        self._magika = magika or Magika()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def identify_path(
        self, path: Path
    ) -> Tuple[MagikaResult, PredictionExplanation]:
        result = self._magika.identify_path(path)
        return result, explain_result(result)

    def identify_paths(
        self, paths: List[Path]
    ) -> List[Tuple[MagikaResult, PredictionExplanation]]:
        results = self._magika.identify_paths(paths)
        return [(r, explain_result(r)) for r in results]

    def identify_bytes(
        self, content: bytes
    ) -> Tuple[MagikaResult, PredictionExplanation]:
        result = self._magika.identify_bytes(content)
        return result, explain_result(result)

    def explain_bytes(self, content: bytes) -> PredictionExplanation:
        """Convenience: return only the explanation."""
        _, explanation = self.identify_bytes(content)
        return explanation

    def explain_path(self, path: Path) -> PredictionExplanation:
        """Convenience: return only the explanation for a file path."""
        _, explanation = self.identify_path(path)
        return explanation
