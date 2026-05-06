"""Label override support for Magika.

Allows users to supply a mapping of file extensions or MIME types to
forced content-type labels, bypassing model inference entirely.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


class LabelOverride:
    """A single override rule: maps an extension or mime to a label."""

    def __init__(self, extension: Optional[str] = None, mime: Optional[str] = None, label: str = "") -> None:
        if not extension and not mime:
            raise ValueError("At least one of 'extension' or 'mime' must be provided.")
        self.extension = extension.lower().lstrip(".") if extension else None
        self.mime = mime.lower() if mime else None
        self.label = label

    def matches_path(self, path: Path) -> bool:
        if self.extension is None:
            return False
        return path.suffix.lower().lstrip(".") == self.extension

    def matches_mime(self, mime: str) -> bool:
        if self.mime is None:
            return False
        return mime.lower() == self.mime

    def __repr__(self) -> str:  # pragma: no cover
        return f"LabelOverride(extension={self.extension!r}, mime={self.mime!r}, label={self.label!r})"


class OverrideEngine:
    """Holds a collection of LabelOverride rules and resolves them."""

    def __init__(self, overrides: Optional[list[LabelOverride]] = None) -> None:
        self._overrides: list[LabelOverride] = overrides or []

    @classmethod
    def from_dict(cls, data: Dict) -> "OverrideEngine":
        """Build an OverrideEngine from a plain dict (e.g. loaded from JSON)."""
        rules = []
        for entry in data.get("overrides", []):
            rules.append(
                LabelOverride(
                    extension=entry.get("extension"),
                    mime=entry.get("mime"),
                    label=entry["label"],
                )
            )
        return cls(rules)

    @classmethod
    def from_json_file(cls, path: Path) -> "OverrideEngine":
        """Load overrides from a JSON file on disk."""
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data)

    def resolve_path(self, path: Path) -> Optional[str]:
        """Return the forced label for *path*, or None if no rule matches."""
        for override in self._overrides:
            if override.matches_path(path):
                return override.label
        return None

    def resolve_mime(self, mime: str) -> Optional[str]:
        """Return the forced label for *mime*, or None if no rule matches."""
        for override in self._overrides:
            if override.matches_mime(mime):
                return override.label
        return None

    def __len__(self) -> int:
        return len(self._overrides)
