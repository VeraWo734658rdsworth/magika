"""Redaction support: mask or replace sensitive labels in MagikaResult objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable

from magika.prediction import MagikaResult


class RedactionError(ValueError):
    """Raised when a redaction rule is misconfigured."""


@dataclass
class RedactionRule:
    """Maps one or more source labels to a replacement label."""

    replacement: str
    labels: frozenset[str] = field(default_factory=frozenset)
    predicate: Callable[[MagikaResult], bool] | None = None

    def __post_init__(self) -> None:
        if not self.replacement or not self.replacement.strip():
            raise RedactionError("replacement must be a non-empty string")
        if not self.labels and self.predicate is None:
            raise RedactionError("at least one of labels or predicate must be provided")
        object.__setattr__(self, "labels", frozenset(self.labels))

    def matches(self, result: MagikaResult) -> bool:
        """Return True if this rule applies to *result*."""
        if self.predicate is not None and self.predicate(result):
            return True
        return result.prediction.dl.ct_label in self.labels

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RedactionRule(replacement={self.replacement!r}, "
            f"labels={set(self.labels)!r})"
        )


@dataclass
class RedactionEngine:
    """Applies an ordered list of RedactionRules to MagikaResult objects."""

    rules: list[RedactionRule] = field(default_factory=list)

    def add_rule(self, rule: RedactionRule) -> None:
        if not isinstance(rule, RedactionRule):
            raise RedactionError(f"expected RedactionRule, got {type(rule).__name__}")
        self.rules.append(rule)

    def redact(self, result: MagikaResult) -> MagikaResult:
        """Return a (possibly relabelled) copy of *result*."""
        for rule in self.rules:
            if rule.matches(result):
                return _relabel(result, rule.replacement)
        return result

    def redact_many(
        self, results: Iterable[MagikaResult]
    ) -> list[MagikaResult]:
        return [self.redact(r) for r in results]


def _relabel(result: MagikaResult, new_label: str) -> MagikaResult:
    """Return a shallow copy of *result* with the ct_label replaced."""
    import copy

    new_result = copy.deepcopy(result)
    new_result.prediction.dl.ct_label = new_label
    if hasattr(new_result.prediction, "output"):
        new_result.prediction.output.ct_label = new_label
    return new_result
