"""Structured report generation for Magika prediction results."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from magika.prediction import MagikaResult


@dataclass
class ReportEntry:
    path: Optional[str]
    label: str
    mime_type: str
    score: float
    group: str

    def to_dict(self) -> Dict:
        return {
            "path": self.path,
            "label": self.label,
            "mime_type": self.mime_type,
            "score": round(self.score, 4),
            "group": self.group,
        }


@dataclass
class Report:
    entries: List[ReportEntry] = field(default_factory=list)

    def add(self, result: MagikaResult, path: Optional[Path] = None) -> None:
        self.entries.append(
            ReportEntry(
                path=str(path) if path is not None else None,
                label=result.dl.ct_label,
                mime_type=result.output.mime_type,
                score=result.output.score,
                group=result.output.group,
            )
        )

    def add_many(
        self, results: List[MagikaResult], paths: Optional[List[Path]] = None
    ) -> None:
        for i, result in enumerate(results):
            p = paths[i] if paths is not None else None
            self.add(result, p)

    def to_dict(self) -> Dict:
        return {"total": len(self.entries), "entries": [e.to_dict() for e in self.entries]}

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def label_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for e in self.entries:
            counts[e.label] = counts.get(e.label, 0) + 1
        return counts

    def filter_by_group(self, group: str) -> "Report":
        filtered = Report()
        filtered.entries = [e for e in self.entries if e.group == group]
        return filtered

    def __len__(self) -> int:
        return len(self.entries)
