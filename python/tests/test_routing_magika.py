"""Tests for routing_magika.py"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.routing import Route, RoutingEngine
from magika.routing_magika import RoutingMagika
from magika.prediction import MagikaResult
from magika.content_types import ContentTypeInfo
from magika.types import Status


def _mock_result(label: str, score: float = 0.95) -> MagikaResult:
    ct = ContentTypeInfo(
        label=label,
        mime_type=f"application/{label}",
        group="code",
        description=label,
        extensions=[f".{label}"],
        is_text=True,
    )
    from magika.prediction import PredictionDetails
    details = PredictionDetails(dl_label=label, dl_score=score, output_label=label, output_score=score)
    return MagikaResult(path=None, status=Status.OK, prediction=details, output=ct)


@pytest.fixture()
def engine():
    inner = MagicMock()
    routing = RoutingEngine()
    routing.add_route(Route("pdf", lambda r: r.output.label == "pdf", "documents"))
    return RoutingMagika(inner=inner, routing_engine=routing)


def test_routing_engine_property(engine):
    assert isinstance(engine.routing_engine, RoutingEngine)


def test_identify_bytes_returns_tuple(engine):
    engine._inner.identify_bytes.return_value = _mock_result("pdf")
    result, handler = engine.identify_bytes(b"%PDF-1.4")
    assert handler == "documents"
    assert result.output.label == "pdf"


def test_identify_bytes_falls_to_default(engine):
    engine._inner.identify_bytes.return_value = _mock_result("python")
    result, handler = engine.identify_bytes(b"print('hello')")
    assert handler == "default"


def test_identify_path_returns_tuple(engine):
    engine._inner.identify_path.return_value = _mock_result("pdf")
    result, handler = engine.identify_path(Path("doc.pdf"))
    assert handler == "documents"


def test_identify_paths_returns_list_of_tuples(engine):
    engine._inner.identify_paths.return_value = [
        _mock_result("pdf"),
        _mock_result("python"),
    ]
    pairs = engine.identify_paths([Path("a.pdf"), Path("b.py")])
    assert len(pairs) == 2
    assert pairs[0][1] == "documents"
    assert pairs[1][1] == "default"


def test_route_many_groups_by_handler(engine):
    engine._inner.identify_paths.return_value = [
        _mock_result("pdf"),
        _mock_result("pdf"),
        _mock_result("python"),
    ]
    groups = engine.route_many([Path("a"), Path("b"), Path("c")])
    assert len(groups["documents"]) == 2
    assert len(groups["default"]) == 1
