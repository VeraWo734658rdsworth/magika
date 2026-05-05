"""Batch processing utilities for Magika."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Generator, Iterable, Iterator, List, Optional, Tuple

from magika.magika import Magika
from magika.prediction import MagikaResult


DEFAULT_BATCH_SIZE = 512
DEFAULT_MAX_WORKERS = min(4, (os.cpu_count() or 1))


def iter_batches(
    items: Iterable[Path], batch_size: int = DEFAULT_BATCH_SIZE
) -> Generator[List[Path], None, None]:
    """Yield successive batches from an iterable of paths."""
    batch: List[Path] = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def process_paths_in_batches(
    magika: Magika,
    paths: Iterable[Path],
    batch_size: int = DEFAULT_BATCH_SIZE,
    max_workers: int = DEFAULT_MAX_WORKERS,
) -> List[Tuple[Path, MagikaResult]]:
    """Process paths in batches, optionally using multiple threads.

    Returns a list of (path, result) tuples preserving input order.
    """
    all_paths = list(paths)
    if not all_paths:
        return []

    results: List[Tuple[Path, MagikaResult]] = []

    if max_workers <= 1:
        for batch in iter_batches(all_paths, batch_size):
            batch_results = magika.identify_paths(batch)
            results.extend(zip(batch, batch_results))
        return results

    batches = list(iter_batches(all_paths, batch_size))
    ordered: List[Optional[List[Tuple[Path, MagikaResult]]]] = [None] * len(batches)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(_process_batch, magika, batch): idx
            for idx, batch in enumerate(batches)
        }
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            ordered[idx] = future.result()

    for batch_result in ordered:
        if batch_result:
            results.extend(batch_result)

    return results


def _process_batch(
    magika: Magika, batch: List[Path]
) -> List[Tuple[Path, MagikaResult]]:
    """Process a single batch and return (path, result) pairs."""
    batch_results = magika.identify_paths(batch)
    return list(zip(batch, batch_results))
