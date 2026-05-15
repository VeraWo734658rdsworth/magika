"""Priority-based result selection for multiple Magika engines."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from magika.prediction import MagikaResult


@dataclass
class PriorityRule:
    """A rule that selects a result based on a predicate, with an associated priority."""

    name: str
    predicate: Callable[[MagikaResult], bool]
    priority: int = 0

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("PriorityRule name must not be empty")

    def matches(self, result: MagikaResult) -> bool:
        return self.predicate(result)

    def __repr__(self) -> str:
        return f"PriorityRule(name={self.name!r}, priority={self.priority})"


@dataclass
class PriorityEngine:
    """Selects among multiple MagikaResults using ordered priority rules."""

    rules: List[PriorityRule] = field(default_factory=list)

    def add_rule(self, rule: PriorityRule) -> None:
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def select(self, results: List[MagikaResult]) -> Optional[MagikaResult]:
        """Return the highest-priority result that matches any rule, or the first result."""
        if not results:
            return None
        for rule in self.rules:
            for result in results:
                if rule.matches(result):
                    return result
        return results[0]

    def select_all_matching(self, results: List[MagikaResult]) -> List[MagikaResult]:
        """Return all results that match at least one rule, ordered by rule priority."""
        matched: List[MagikaResult] = []
        seen_ids = set()
        for rule in self.rules:
            for result in results:
                rid = id(result)
                if rule.matches(result) and rid not in seen_ids:
                    matched.append(result)
                    seen_ids.add(rid)
        return matched
