"""Tests for routing.py"""
from __future__ import annotations

import pytest

from magika.routing import Route, RoutingEngine, RoutingError
from magika.prediction import MagikaResult
from magika.content_types import ContentTypeInfo
from magika.types import Status


def _make_result(label: str, score: float = 0.9) -> MagikaResult:
    ct = ContentTypeInfo(
        label=label,
        mime_type=f"application/{label}",
        group="code",
        description=label,
        extensions=[f".{label}"],
        is_text=False,
    )
    from magika.prediction import PredictionDetails
    details = PredictionDetails(dl_label=label, dl_score=score, output_label=label, output_score=score)
    return MagikaResult(path=None, status=Status.OK, prediction=details, output=ct)


class TestRoute:
    def test_empty_name_raises(self):
        with pytest.raises(RoutingError):
            Route(name="", predicate=lambda r: True, handler="h")

    def test_empty_handler_raises(self):
        with pytest.raises(RoutingError):
            Route(name="r", predicate=lambda r: True, handler="")

    def test_matches_delegates_to_predicate(self):
        result = _make_result("python")
        route = Route(name="py", predicate=lambda r: r.output.label == "python", handler="code")
        assert route.matches(result) is True

    def test_no_match(self):
        result = _make_result("pdf")
        route = Route(name="py", predicate=lambda r: r.output.label == "python", handler="code")
        assert route.matches(result) is False

    def test_repr_contains_name_and_handler(self):
        route = Route(name="py", predicate=lambda r: True, handler="code")
        assert "py" in repr(route)
        assert "code" in repr(route)


class TestRoutingEngine:
    def test_default_handler_is_default(self):
        engine = RoutingEngine()
        assert engine.default_handler == "default"

    def test_set_default_handler(self):
        engine = RoutingEngine()
        engine.set_default_handler("fallback")
        assert engine.default_handler == "fallback"

    def test_set_empty_default_raises(self):
        engine = RoutingEngine()
        with pytest.raises(RoutingError):
            engine.set_default_handler("")

    def test_route_returns_default_when_no_routes(self):
        engine = RoutingEngine()
        result = _make_result("pdf")
        assert engine.route(result) == "default"

    def test_route_matches_first_matching_route(self):
        engine = RoutingEngine()
        engine.add_route(Route("pdf", lambda r: r.output.label == "pdf", "documents"))
        engine.add_route(Route("any", lambda r: True, "catch_all"))
        assert engine.route(_make_result("pdf")) == "documents"
        assert engine.route(_make_result("python")) == "catch_all"

    def test_route_many_groups_correctly(self):
        engine = RoutingEngine()
        engine.add_route(Route("pdf", lambda r: r.output.label == "pdf", "docs"))
        results = [_make_result("pdf"), _make_result("python"), _make_result("pdf")]
        groups = engine.route_many(results)
        assert len(groups["docs"]) == 2
        assert len(groups["default"]) == 1

    def test_route_count(self):
        engine = RoutingEngine()
        assert engine.route_count() == 0
        engine.add_route(Route("r1", lambda r: True, "h"))
        assert engine.route_count() == 1
