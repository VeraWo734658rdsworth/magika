"""Reporting utilities for batch processing results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from magika.prediction import MagikaResult
from magika.types import Status


def summarize_batch_results(
    results: List[Tuple[Path, MagikaResult]],
) -> Dict[str, int]:
    """Return a dict mapping content-type label -> count."""
    counts: Dict[str, int] = {}
    for _path, result in results:
        label = result.output.ct_label
        counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def count_errors(results: List[Tuple[Path, MagikaResult]]) -> int:
    """Count results where status is not OK."""
    return sum(
        1 for _p, r in results if r.status != Status.OK
    )


def print_batch_text_report(
    results: List[Tuple[Path, MagikaResult]], verbose: bool = False
) -> None:
    """Print a human-readable summary of batch results."""
    summary = summarize_batch_results(results)
    errors = count_errors(results)
    total = len(results)

    print(f"Processed {total} file(s), {errors} error(s).")
    print("\nContent-type breakdown:")
    for label, count in summary.items():
        pct = 100.0 * count / total if total else 0.0
        print(f"  {label:<30} {count:>6}  ({pct:.1f}%)")

    if verbose:
        print("\nPer-file results:")
        for path, result in results:
            print(f"  {path}: {result.output.ct_label} [{result.status}]")


def print_batch_json_report(
    results: List[Tuple[Path, MagikaResult]],
) -> None:
    """Print a JSON summary of batch results."""
    summary = summarize_batch_results(results)
    errors = count_errors(results)
    report = {
        "total": len(results),
        "errors": errors,
        "breakdown": summary,
    }
    print(json.dumps(report, indent=2))
