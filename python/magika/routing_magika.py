"""RoutingMagika: wraps a MagikaLike and attaches routing metadata to results."""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from magika.pipeline import MagikaLike
from magika.prediction import MagikaResult
from magika.routing import RoutingEngine


class RoutingMagika:
    """Delegates identification to an inner engine and routes each result."""

    def __init__(self, inner: MagikaLike, engine: RoutingEngine) -> None:
        self._inner = inner
        self._engine = engine

    @property
    def routing_engine(self) -> RoutingEngine:
        return self._engine

    def identify_bytes(self, data: bytes) -> Tuple[MagikaResult, str]:
        result = self._inner.identify_bytes(data)
        return result, self._engine.route(result)

    def identify_path(self, path: Path) -> Tuple[MagikaResult, str]:
        result = self._inner.identify_path(path)
        return result, self._engine.route(result)

    def identify_paths(
        self, paths: List[Path]
    ) -> List[Tuple[MagikaResult, str]]:
        results = self._inner.identify_paths(paths)
        return [(r, self._engine.route(r)) for r in results]

    def route_many(
        self, paths: List[Path]
    ) -> dict:
        results = self._inner.identify_paths(paths)
        return self._engine.route_many(results)
