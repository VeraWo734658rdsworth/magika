"""Fluent builder for constructing a Magika Pipeline."""
from __future__ import annotations

from typing import List, Optional

from magika.pipeline import MagikaLike, Pipeline, PipelineError


class PipelineBuilder:
    """Fluent interface for assembling a :class:`Pipeline`.

    Example::

        pipeline = (
            PipelineBuilder(base_engine)
            .then(audit_engine)
            .then(filter_engine)
            .build()
        )
    """

    def __init__(self, first: MagikaLike) -> None:
        if not isinstance(first, MagikaLike):
            raise PipelineError(
                f"First stage must implement MagikaLike: {first!r}"
            )
        self._stages: List[MagikaLike] = [first]

    def then(self, stage: MagikaLike) -> "PipelineBuilder":
        """Append *stage* to the pipeline and return *self* for chaining."""
        if not isinstance(stage, MagikaLike):
            raise PipelineError(
                f"Stage must implement MagikaLike: {stage!r}"
            )
        self._stages.append(stage)
        return self

    def build(self) -> Pipeline:
        """Return the assembled :class:`Pipeline`."""
        return Pipeline(list(self._stages))

    @property
    def stage_count(self) -> int:
        return len(self._stages)

    def __repr__(self) -> str:
        names = " -> ".join(type(s).__name__ for s in self._stages)
        return f"PipelineBuilder([{names}])"
