"""Magika wrapper that clamps prediction scores to a configurable range."""
from __future__ import annotations

from pathlib import Path
from typing import List, Sequence

from magika.clamp import ClampPolicy, clamp_result
from magika.pipeline import MagikaLike
from magika.prediction import MagikaResult


class ClampMagika:
    """Wraps any *MagikaLike* and clamps every returned score.

    Parameters
    ----------
    inner:
        The underlying identification engine.
    policy:
        Score clamping policy.  Defaults to the identity range ``[0, 1]``.
    """

    def __init__(
        self,
        inner: MagikaLike,
        policy: ClampPolicy | None = None,
    ) -> None:
        self._inner = inner
        self._policy = policy or ClampPolicy()

    @property
    def policy(self) -> ClampPolicy:
        return self._policy

    def identify_bytes(self, data: bytes) -> MagikaResult:
        result = self._inner.identify_bytes(data)
        return clamp_result(result, self._policy)

    def identify_path(self, path: Path) -> MagikaResult:
        result = self._inner.identify_path(path)
        return clamp_result(result, self._policy)

    def identify_paths(self, paths: Sequence[Path]) -> List[MagikaResult]:
        results = self._inner.identify_paths(paths)
        return [clamp_result(r, self._policy) for r in results]
