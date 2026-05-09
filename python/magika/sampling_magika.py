"""Magika wrapper that samples inputs before delegating to an inner engine."""
from __future__ import annotations

from pathlib import Path
from typing import List, Sequence

from magika.magika import Magika
from magika.prediction import MagikaResult
from magika.sampling import SamplingPolicy, sample_bytes_inputs, sample_paths


class SamplingMagika:
    """Wraps a :class:`Magika` instance and limits inputs via a :class:`SamplingPolicy`.

    Paths or byte strings that exceed *policy.max_samples* are silently
    dropped (a random subset is kept).  This is useful for quick surveys of
    large directory trees.
    """

    def __init__(self, inner: Magika, policy: SamplingPolicy) -> None:
        self._inner = inner
        self._policy = policy

    @property
    def policy(self) -> SamplingPolicy:
        return self._policy

    def identify_bytes(self, content: bytes) -> MagikaResult:
        """Delegate directly — sampling does not apply to single items."""
        return self._inner.identify_bytes(content)

    def identify_path(self, path: Path) -> MagikaResult:
        """Delegate directly — sampling does not apply to single items."""
        return self._inner.identify_path(path)

    def identify_paths(self, paths: Sequence[Path]) -> List[MagikaResult]:
        """Sample *paths* then delegate to the inner engine."""
        sampled = sample_paths(list(paths), self._policy)
        return self._inner.identify_paths(sampled)

    def identify_bytes_batch(
        self, inputs: Sequence[bytes]
    ) -> List[MagikaResult]:
        """Sample *inputs* then identify each entry."""
        sampled = sample_bytes_inputs(list(inputs), self._policy)
        return [self._inner.identify_bytes(b) for b in sampled]
