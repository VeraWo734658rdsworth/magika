"""Schema validation for Magika results and configuration objects."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class SchemaValidationError(ValueError):
    """Raised when a result or config dict fails schema validation."""

    def __init__(self, message: str, path: str = "") -> None:
        self.path = path
        super().__init__(f"[{path}] {message}" if path else message)


@dataclass
class FieldSpec:
    """Specification for a single field in a schema."""

    name: str
    expected_type: type
    required: bool = True
    nullable: bool = False
    allowed_values: Optional[List[Any]] = field(default=None)

    def validate(self, data: Dict[str, Any], parent_path: str = "") -> None:
        path = f"{parent_path}.{self.name}" if parent_path else self.name
        if self.name not in data:
            if self.required:
                raise SchemaValidationError(f"missing required field '{self.name}'", path)
            return
        value = data[self.name]
        if value is None:
            if not self.nullable:
                raise SchemaValidationError("field must not be None", path)
            return
        if not isinstance(value, self.expected_type):
            raise SchemaValidationError(
                f"expected {self.expected_type.__name__}, got {type(value).__name__}", path
            )
        if self.allowed_values is not None and value not in self.allowed_values:
            raise SchemaValidationError(
                f"value {value!r} not in allowed set {self.allowed_values}", path
            )


@dataclass
class ResultSchema:
    """Schema that validates a Magika result dictionary."""

    fields: List[FieldSpec] = field(default_factory=list)

    def validate(self, data: Dict[str, Any], path: str = "") -> None:
        if not isinstance(data, dict):
            raise SchemaValidationError("expected a dict", path)
        for spec in self.fields:
            spec.validate(data, path)

    def validate_many(self, items: List[Dict[str, Any]]) -> None:
        for idx, item in enumerate(items):
            self.validate(item, path=f"[{idx}]")


DEFAULT_RESULT_SCHEMA = ResultSchema(
    fields=[
        FieldSpec("label", str),
        FieldSpec("score", float),
        FieldSpec("mime_type", str, nullable=True),
        FieldSpec("group", str, nullable=True),
    ]
)
