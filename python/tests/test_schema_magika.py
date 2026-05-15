"""Tests for SchemaMagika wrapper."""
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.schema import ResultSchema, FieldSpec, SchemaValidationError
from magika.schema_magika import SchemaMagika


def _mock_result(label="python", score=0.95, mime_type="text/x-python", group="text"):
    pred = MagicMock()
    pred.label = label
    pred.score = score
    pred.mime_type = mime_type
    pred.group = group
    result = MagicMock()
    result.prediction = pred
    return result


@pytest.fixture()
def mock_magika():
    return MagicMock()


@pytest.fixture()
def engine(mock_magika):
    return SchemaMagika(mock_magika)


def test_schema_property_returns_default(engine):
    assert engine.schema is not None
    field_names = {f.name for f in engine.schema.fields}
    assert "label" in field_names


def test_custom_schema_stored(mock_magika):
    custom = ResultSchema(fields=[FieldSpec("label", str)])
    eng = SchemaMagika(mock_magika, schema=custom)
    assert eng.schema is custom


def test_identify_bytes_passes_valid_result(mock_magika, engine):
    mock_magika.identify_bytes.return_value = _mock_result()
    result = engine.identify_bytes(b"print('hi')")
    assert result.prediction.label == "python"


def test_identify_path_passes_valid_result(mock_magika, engine):
    mock_magika.identify_path.return_value = _mock_result(label="pdf")
    result = engine.identify_path(Path("doc.pdf"))
    assert result.prediction.label == "pdf"


def test_identify_paths_passes_valid_results(mock_magika, engine):
    paths = [Path("a.py"), Path("b.pdf")]
    mock_magika.identify_paths.return_value = [_mock_result(), _mock_result(label="pdf")]
    results = engine.identify_paths(paths)
    assert len(results) == 2


def test_identify_bytes_raises_on_bad_schema(mock_magika):
    strict = ResultSchema(fields=[FieldSpec("label", str, allowed_values=["pdf", "zip"])])
    eng = SchemaMagika(mock_magika, schema=strict)
    mock_magika.identify_bytes.return_value = _mock_result(label="python")
    with pytest.raises(SchemaValidationError):
        eng.identify_bytes(b"data")


def test_identify_path_includes_path_in_error(mock_magika):
    strict = ResultSchema(fields=[FieldSpec("score", float, allowed_values=[1.0])])
    eng = SchemaMagika(mock_magika, schema=strict)
    mock_magika.identify_path.return_value = _mock_result(score=0.5)
    with pytest.raises(SchemaValidationError, match="test.py"):
        eng.identify_path(Path("test.py"))


def test_identify_paths_raises_for_bad_item(mock_magika, engine):
    bad = _mock_result()
    bad.prediction.score = "not-a-float"
    mock_magika.identify_paths.return_value = [_mock_result(), bad]
    with pytest.raises(SchemaValidationError):
        engine.identify_paths([Path("a.py"), Path("b.py")])
