"""Magika wrapper that persists results to a checkpoint file."""
from __future__ import annotations

from pathlib import Path

from magika.checkpoint import Checkpoint, CheckpointEntry
from magika.pipeline import MagikaLike
from magika.prediction import MagikaResult


class CheckpointMagika:
    """Wraps a MagikaLike engine and records each result to a Checkpoint.

    Results are accumulated in memory and can be flushed to disk at any time
    via :meth:`save`.  An existing checkpoint file is loaded on construction
    so that interrupted runs can be resumed.
    """

    def __init__(self, inner: MagikaLike, checkpoint_path: Path) -> None:
        self._inner = inner
        self._checkpoint_path = checkpoint_path
        if checkpoint_path.exists():
            self._checkpoint = Checkpoint.load(checkpoint_path)
        else:
            self._checkpoint = Checkpoint()

    @property
    def checkpoint(self) -> Checkpoint:
        return self._checkpoint

    def _record(self, result: MagikaResult, path: str | None = None) -> MagikaResult:
        entry = CheckpointEntry(
            label=result.output.ct_label,
            score=result.output.score,
            path=path,
        )
        self._checkpoint.add(entry)
        return result

    def identify_bytes(self, content: bytes) -> MagikaResult:
        result = self._inner.identify_bytes(content)
        return self._record(result)

    def identify_path(self, path: Path) -> MagikaResult:
        result = self._inner.identify_path(path)
        return self._record(result, str(path))

    def identify_paths(self, paths: list[Path]) -> list[MagikaResult]:
        results = self._inner.identify_paths(paths)
        for p, r in zip(paths, results):
            self._record(r, str(p))
        return results

    def save(self) -> None:
        """Flush the in-memory checkpoint to disk."""
        self._checkpoint.save(self._checkpoint_path)

    def __repr__(self) -> str:
        return (
            f"CheckpointMagika(inner={self._inner!r}, "
            f"entries={len(self._checkpoint)})"
        )
