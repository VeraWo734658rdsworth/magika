"""Magika wrapper that records per-call timing into a ProfilingSession."""

from __future__ import annotations

from pathlib import Path
from typing import List

from magika.magika import Magika
from magika.prediction import MagikaResult
from magika.profile import ProfilingSession, Timer


class ProfileMagika:
    """Wraps a Magika instance and records timing for every identification call."""

    def __init__(self, magika: Magika) -> None:
        self._magika = magika
        self._session = ProfilingSession()

    @property
    def session(self) -> ProfilingSession:
        return self._session

    def identify_path(self, path: Path) -> MagikaResult:
        with Timer() as t:
            result = self._magika.identify_path(path)
        self._session.record(
            path=path,
            label=result.prediction.label,
            elapsed_ms=t.elapsed_ms,
        )
        return result

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        with Timer() as t:
            results = self._magika.identify_paths(paths)
        for path, result in zip(paths, results):
            self._session.record(
                path=path,
                label=result.prediction.label,
                elapsed_ms=t.elapsed_ms / max(len(paths), 1),
            )
        return results

    def identify_bytes(self, content: bytes) -> MagikaResult:
        with Timer() as t:
            result = self._magika.identify_bytes(content)
        self._session.record(
            path=None,
            label=result.prediction.label,
            elapsed_ms=t.elapsed_ms,
        )
        return result

    def clear_profile(self) -> None:
        self._session.clear()
