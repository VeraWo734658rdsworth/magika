"""Utilities for formatting and printing PredictionStats."""

from __future__ import annotations

import json
from typing import TextIO
import sys

from magika.stats import PredictionStats


def _sorted_counts(counts: dict) -> list[tuple[str, int]]:
    """Return label/group counts sorted by frequency descending."""
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)


def print_text_report(stats: PredictionStats, file: TextIO = sys.stdout) -> None:
    """Print a human-readable summary of prediction statistics."""
    print(f"Total files analyzed : {stats.total}", file=file)
    print(f"Average confidence   : {stats.average_score:.2%}", file=file)
    print(
        f"Low-confidence files : {stats.low_confidence_count} "
        f"(threshold={stats.low_confidence_threshold:.0%})",
        file=file,
    )

    if stats.total == 0:
        return

    print("\nTop content types:", file=file)
    for label, count in _sorted_counts(stats.label_counts)[:10]:
        pct = count / stats.total * 100
        print(f"  {label:<30} {count:>6}  ({pct:.1f}%)", file=file)

    print("\nBreakdown by group:", file=file)
    for group, count in _sorted_counts(stats.group_counts):
        pct = count / stats.total * 100
        print(f"  {group:<20} {count:>6}  ({pct:.1f}%)", file=file)


def print_json_report(
    stats: PredictionStats,
    file: TextIO = sys.stdout,
    indent: int = 2,
) -> None:
    """Print statistics as a JSON document."""
    data = stats.to_dict()
    # Sort counts for deterministic output
    data["label_counts"] = dict(_sorted_counts(data["label_counts"]))
    data["group_counts"] = dict(_sorted_counts(data["group_counts"]))
    print(json.dumps(data, indent=indent), file=file)


def format_summary_line(stats: PredictionStats) -> str:
    """Return a compact single-line summary string."""
    if stats.total == 0:
        return "No files analyzed."
    return (
        f"{stats.total} file(s) | "
        f"avg confidence: {stats.average_score:.1%} | "
        f"top label: {stats.most_common_label} | "
        f"low confidence: {stats.low_confidence_count}"
    )
