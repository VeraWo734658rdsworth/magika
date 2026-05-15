"""Magika wrapper that validates results against a schema before returning them."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from magika.pipeline import MagikaLike
from magika.prediction import MagikaResult
from magika.schema import DEFAULT_RESULT_SCHEMA, ResultSchema, SchemaValidationError


class SchemaMagika:
    """Wraps a MagikaLike engine and validates every result against a schema.

    Raises :class:`SchemaValidationError` if any result dict fails validation.
    """

    def __init__(
        self,
        inner: MagikaLike,
        schema: Optional[ResultSchema] = None,
    ) -> None:
        self._inner = inner
        self._schema = schema or DEFAULT_RESULT_SCHEMA

    @property
    def schema(self) -> ResultSchema:
        return self._schema

    def _validate(self, result: MagikaResult, path: str = "") -> MagikaResult:
        data = {
            "label": result.prediction.label if result.prediction else None,
            "score": result.prediction.score if result.prediction else None,
            "mime_type": result.prediction.mime_type if result.prediction else None,
            "group": result.prediction.group if result.prediction else None,
        }
        self._schema.validate(data, path)
        return result

    def identify_bytes(self, content: bytes) -> MagikaResult:
        result = self._inner.identify_bytes(content)
        return self._validate(result, path="identify_bytes")

    def identify_path(self, path: Path) -> MagikaResult:
        result = self._inner.identify_path(path)
        return self._validate(result, path=str(path))

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        results = self._inner.identify_paths(paths)
        for p, r in zip(paths, results):
            self._validate(r, path=str(p))
        return results
