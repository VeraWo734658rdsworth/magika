"""Audit log for magika predictions.

Records identification results to a structured log for later analysis
or compliance review.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import IO, Iterable, Optional

from magika.prediction import MagikaResult


class AuditEntry:
    """A single audit record for one identification."""

    def __init__(self, path: Optional[str], label: str, score: float, timestamp: float) -> None:
        self.path = path
        self.label = label
        self.score = score
        self.timestamp = timestamp

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "label": self.label,
            "score": round(self.score, 6),
            "timestamp": self.timestamp,
        }

    def __repr__(self) -> str:
        return f"AuditEntry(path={self.path!r}, label={self.label!r}, score={self.score:.4f})"


class AuditLogger:
    """Writes prediction audit entries to a newline-delimited JSON stream."""

    def __init__(self, stream: IO[str]) -> None:
        self._stream = stream
        self._count = 0

    @property
    def count(self) -> int:
        return self._count

    def log_result(self, result: MagikaResult, path: Optional[str] = None) -> AuditEntry:
        entry = AuditEntry(
            path=path,
            label=result.prediction.label,
            score=result.prediction.score,
            timestamp=time.time(),
        )
        self._stream.write(json.dumps(entry.to_dict()) + "\n")
        self._count += 1
        return entry

    def log_results(self, results: Iterable[MagikaResult], paths: Optional[Iterable[Optional[str]]] = None) -> list[AuditEntry]:
        path_iter = iter(paths) if paths is not None else iter([])
        entries: list[AuditEntry] = []
        for result in results:
            path = next(path_iter, None)
            entries.append(self.log_result(result, path=path))
        return entries


def load_audit_log(stream: IO[str]) -> list[AuditEntry]:
    """Parse a newline-delimited JSON audit log back into AuditEntry objects."""
    entries: list[AuditEntry] = []
    for line in stream:
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        entries.append(AuditEntry(
            path=data.get("path"),
            label=data["label"],
            score=data["score"],
            timestamp=data["timestamp"],
        ))
    return entries
