"""Magika wrapper that runs multiple inner engines and picks the best result."""
from __future__ import annotations

from pathlib import Path
from typing import List

from magika.prediction import MagikaResult
from magika.priority import PriorityEngine, PriorityRule


class PriorityMagika:
    """Delegates to multiple Magika-compatible engines and selects a result via PriorityEngine."""

    def __init__(self, engines: List, priority_engine: PriorityEngine | None = None) -> None:
        if not engines:
            raise ValueError("At least one engine must be provided")
        self._engines = list(engines)
        self._priority = priority_engine or PriorityEngine()

    @property
    def priority_engine(self) -> PriorityEngine:
        return self._priority

    def identify_bytes(self, content: bytes) -> MagikaResult:
        results = [e.identify_bytes(content) for e in self._engines]
        result = self._priority.select(results)
        assert result is not None
        return result

    def identify_path(self, path: Path) -> MagikaResult:
        results = [e.identify_path(path) for e in self._engines]
        result = self._priority.select(results)
        assert result is not None
        return result

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        if not paths:
            return []
        per_engine = [e.identify_paths(paths) for e in self._engines]
        selected: List[MagikaResult] = []
        for i in range(len(paths)):
            candidates = [per_engine[e][i] for e in range(len(self._engines))]
            result = self._priority.select(candidates)
            assert result is not None
            selected.append(result)
        return selected
