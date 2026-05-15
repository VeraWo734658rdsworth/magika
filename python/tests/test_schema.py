"""Unit tests for magika.schema."""
import pytest

from magika.schema import (
    DEFAULT_RESULT_SCHEMA,
    FieldSpec,
    ResultSchema,
    SchemaValidationError,
)


def test_field_spec_passes_valid_data():
    spec = FieldSpec("score", float)
    spec.validate({"score": 0.9})  # should not raise


def test_field_spec_raises_on_missing_required():
    spec = FieldSpec("label", str, required=True)
    with pytest.raises(SchemaValidationError, match="missing required field"):
        spec.validate({})


def test_field_spec_optional_field_missing_is_ok():
    spec = FieldSpec("group", str, required=False)
    spec.validate({})  # should not raise


def test_field_spec_raises_on_wrong_type():
    spec = FieldSpec("score", float)
    with pytest.raises(SchemaValidationError, match="expected float"):
        spec.validate({"score": "high"})


def test_field_spec_nullable_none_passes():
    spec = FieldSpec("mime_type", str, nullable=True)
    spec.validate({"mime_type": None})  # should not raise


def test_field_spec_non_nullable_none_raises():
    spec = FieldSpec("label", str, nullable=False)
    with pytest.raises(SchemaValidationError, match="must not be None"):
        spec.validate({"label": None})


def test_field_spec_allowed_values_passes():
    spec = FieldSpec("group", str, allowed_values=["text", "binary", "image"])
    spec.validate({"group": "text"})  # should not raise


def test_field_spec_allowed_values_raises():
    spec = FieldSpec("group", str, allowed_values=["text", "binary"])
    with pytest.raises(SchemaValidationError, match="not in allowed set"):
        spec.validate({"group": "video"})


def test_schema_validate_passes_complete_dict():
    schema = ResultSchema(fields=[FieldSpec("label", str), FieldSpec("score", float)])
    schema.validate({"label": "python", "score": 0.99})


def test_schema_validate_raises_on_non_dict():
    schema = ResultSchema(fields=[FieldSpec("label", str)])
    with pytest.raises(SchemaValidationError, match="expected a dict"):
        schema.validate(["label", "python"])


def test_schema_validate_many_passes():
    schema = ResultSchema(fields=[FieldSpec("label", str)])
    schema.validate_many([{"label": "pdf"}, {"label": "zip"}])


def test_schema_validate_many_raises_with_index():
    schema = ResultSchema(fields=[FieldSpec("score", float)])
    with pytest.raises(SchemaValidationError, match=r"\[1\]"):
        schema.validate_many([{"score": 0.8}, {"score": "bad"}])


def test_default_result_schema_has_expected_fields():
    names = {f.name for f in DEFAULT_RESULT_SCHEMA.fields}
    assert {"label", "score", "mime_type", "group"}.issubset(names)


def test_error_path_included_in_message():
    spec = FieldSpec("label", str)
    try:
        spec.validate({}, parent_path="root")
    except SchemaValidationError as exc:
        assert "root" in str(exc)
        assert exc.path == "root.label"
