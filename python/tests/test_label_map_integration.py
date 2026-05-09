"""Integration-style tests for LabelMap + LabelMapMagika working together."""
from __future__ import annotations

from unittest.mock import MagicMock

from magika.label_map import LabelMap
from magika.label_map_magika import LabelMapMagika


def _mock_result(label: str) -> MagicMock:
    result = MagicMock()
    result.prediction.output.ct_label = label
    return result


def _make_engine(mapping: dict) -> tuple[LabelMapMagika, MagicMock]:
    inner = MagicMock()
    lm = LabelMap.from_dict(mapping)
    engine = LabelMapMagika(inner=inner, label_map=lm)
    return engine, inner


def test_many_to_one_grouping():
    """Multiple source labels can map to the same target."""
    engine, inner = _make_engine({
        "pdf": "document",
        "docx": "document",
        "odt": "document",
    })
    for src in ("pdf", "docx", "odt"):
        inner.identify_bytes.return_value = _mock_result(src)
        result = engine.identify_bytes(b"data")
        assert result.prediction.output.ct_label == "document"


def test_chained_maps_are_not_transitive():
    """Mapping a -> b and b -> c does NOT chain; only direct mappings apply."""
    engine, inner = _make_engine({"a": "b", "b": "c"})
    inner.identify_bytes.return_value = _mock_result("a")
    result = engine.identify_bytes(b"")
    # 'a' maps to 'b'; 'b' is not re-resolved.
    assert result.prediction.output.ct_label == "b"


def test_empty_map_is_identity():
    engine, inner = _make_engine({})
    inner.identify_bytes.return_value = _mock_result("python")
    result = engine.identify_bytes(b"")
    assert result.prediction.output.ct_label == "python"


def test_identify_paths_mixed_mapped_and_unmapped():
    engine, inner = _make_engine({"javascript": "js"})
    inner.identify_paths.return_value = [
        _mock_result("javascript"),
        _mock_result("shell"),
        _mock_result("javascript"),
    ]
    results = engine.identify_paths([])
    labels = [r.prediction.output.ct_label for r in results]
    assert labels == ["js", "shell", "js"]


def test_label_map_len_reflects_additions():
    lm = LabelMap()
    assert len(lm) == 0
    lm.add("pdf", "doc")
    assert len(lm) == 1
    lm.add("docx", "doc")
    assert len(lm) == 2
