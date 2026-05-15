"""Label-based routing: dispatch results to different handlers based on label or group."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from magika.prediction import MagikaResult


class RoutingError(Exception):
    """Raised when routing configuration is invalid."""


@dataclass
class Route:
    """A single routing rule mapping a predicate to a handler name."""

    name: str
    predicate: Callable[[MagikaResult], bool]
    handler: str

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise RoutingError("Route name must not be empty.")
        if not self.handler or not self.handler.strip():
            raise RoutingError("Route handler must not be empty.")

    def matches(self, result: MagikaResult) -> bool:
        return self.predicate(result)

    def __repr__(self) -> str:
        return f"Route(name={self.name!r}, handler={self.handler!r})"


@dataclass
class RoutingEngine:
    """Dispatches a MagikaResult to a handler name using ordered routes."""

    _routes: List[Route] = field(default_factory=list)
    _default_handler: str = "default"

    @property
    def default_handler(self) -> str:
        return self._default_handler

    def set_default_handler(self, handler: str) -> None:
        if not handler or not handler.strip():
            raise RoutingError("Default handler must not be empty.")
        self._default_handler = handler

    def add_route(self, route: Route) -> None:
        self._routes.append(route)

    def route(self, result: MagikaResult) -> str:
        for r in self._routes:
            if r.matches(result):
                return r.handler
        return self._default_handler

    def route_many(self, results: List[MagikaResult]) -> Dict[str, List[MagikaResult]]:
        groups: Dict[str, List[MagikaResult]] = {}
        for result in results:
            handler = self.route(result)
            groups.setdefault(handler, []).append(result)
        return groups

    def route_count(self) -> int:
        return len(self._routes)
