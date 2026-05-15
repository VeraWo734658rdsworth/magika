"""Checkpoint support for saving and restoring Magika pipeline state."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class CheckpointError(Exception):
    """Raised when a checkpoint cannot be saved or loaded."""


@dataclass
class CheckpointEntry:
    label: str
    score: float
    path: str | None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "score": round(self.score, 6),
            "path": self.path,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CheckpointEntry":
        return cls(
            label=data["label"],
            score=data["score"],
            path=data.get("path"),
            timestamp=data.get("timestamp", 0.0),
        )

    def __repr__(self) -> str:
        return f"CheckpointEntry(label={self.label!r}, score={self.score:.4f})"


@dataclass
class Checkpoint:
    entries: list[CheckpointEntry] = field(default_factory=list)

    def add(self, entry: CheckpointEntry) -> None:
        self.entries.append(entry)

    def save(self, path: Path) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            data = {"entries": [e.to_dict() for e in self.entries]}
            path.write_text(json.dumps(data, indent=2))
        except OSError as exc:
            raise CheckpointError(f"Failed to save checkpoint to {path}: {exc}") from exc

    @classmethod
    def load(cls, path: Path) -> "Checkpoint":
        try:
            raw = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise CheckpointError(f"Failed to load checkpoint from {path}: {exc}") from exc
        entries = [CheckpointEntry.from_dict(e) for e in raw.get("entries", [])]
        return cls(entries=entries)

    def __len__(self) -> int:
        return len(self.entries)

    def __repr__(self) -> str:
        return f"Checkpoint(entries={len(self.entries)})"
