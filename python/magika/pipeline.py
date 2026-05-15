"""Composable pipeline for chaining multiple Magika wrappers."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Protocol, runtime_checkable

from magika.prediction import MagikaResult


@runtime_checkable
class MagikaLike(Protocol):
    def identify_bytes(self, content: bytes) -> MagikaResult: ...
    def identify_path(self, path: Path) -> MagikaResult: ...
    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]: ...


class PipelineError(Exception):
    """Raised when the pipeline is misconfigured."""


@dataclass
class Pipeline:
    """Chain a sequence of MagikaLike stages, passing results through each.

    Each stage receives the *same* raw input (bytes / path) and the result
    of the *previous* stage is ignored — the final stage's result is
    returned.  Stages are useful for side-effects (audit, profiling, etc.)
    or for wrapping (override, filter, etc.) where each wrapper already
    delegates to an inner engine internally.

    For a purely decorating chain just wrap the stages:
        Pipeline([AuditMagika(RetryMagika(base))])
    """

    stages: List[MagikaLike] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.stages:
            raise PipelineError("Pipeline requires at least one stage.")
        for i, stage in enumerate(self.stages):
            if not isinstance(stage, MagikaLike):
                raise PipelineError(
                    f"Stage {i} does not implement MagikaLike: {stage!r}"
                )

    @property
    def head(self) -> MagikaLike:
        return self.stages[0]

    @property
    def tail(self) -> MagikaLike:
        return self.stages[-1]

    def identify_bytes(self, content: bytes) -> MagikaResult:
        result = None
        for stage in self.stages:
            result = stage.identify_bytes(content)
        return result  # type: ignore[return-value]

    def identify_path(self, path: Path) -> MagikaResult:
        result = None
        for stage in self.stages:
            result = stage.identify_path(path)
        return result  # type: ignore[return-value]

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        result: List[MagikaResult] = []
        for stage in self.stages:
            result = stage.identify_paths(paths)
        return result

    def __len__(self) -> int:
        return len(self.stages)

    def __repr__(self) -> str:
        names = " -> ".join(type(s).__name__ for s in self.stages)
        return f"Pipeline([{names}])"
