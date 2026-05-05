"""Tests for batch processing utilities."""

from __future__ import annotations

from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from magika.batch import (
    DEFAULT_BATCH_SIZE,
    _process_batch,
    iter_batches,
    process_paths_in_batches,
)


def _make_paths(n: int) -> List[Path]:
    return [Path(f"/tmp/file_{i}.bin") for i in range(n)]


def _make_mock_result(label: str = "text") -> MagicMock:
    result = MagicMock()
    result.output.ct_label = label
    return result


# ---------------------------------------------------------------------------
# iter_batches
# ---------------------------------------------------------------------------

def test_iter_batches_empty():
    batches = list(iter_batches([], batch_size=10))
    assert batches == []


def test_iter_batches_single_batch():
    paths = _make_paths(5)
    batches = list(iter_batches(paths, batch_size=10))
    assert len(batches) == 1
    assert batches[0] == paths


def test_iter_batches_exact_multiple():
    paths = _make_paths(10)
    batches = list(iter_batches(paths, batch_size=5))
    assert len(batches) == 2
    assert len(batches[0]) == 5
    assert len(batches[1]) == 5


def test_iter_batches_remainder():
    paths = _make_paths(11)
    batches = list(iter_batches(paths, batch_size=5))
    assert len(batches) == 3
    assert len(batches[2]) == 1


# ---------------------------------------------------------------------------
# process_paths_in_batches
# ---------------------------------------------------------------------------

def test_process_paths_empty():
    magika = MagicMock()
    result = process_paths_in_batches(magika, [], batch_size=10, max_workers=1)
    assert result == []
    magika.identify_paths.assert_not_called()


def test_process_paths_single_worker():
    paths = _make_paths(3)
    mock_results = [_make_mock_result() for _ in paths]
    magika = MagicMock()
    magika.identify_paths.return_value = mock_results

    output = process_paths_in_batches(magika, paths, batch_size=10, max_workers=1)

    assert len(output) == 3
    assert [p for p, _ in output] == paths


def test_process_paths_multi_worker_order():
    paths = _make_paths(20)
    magika = MagicMock()
    magika.identify_paths.side_effect = lambda batch: [
        _make_mock_result("text") for _ in batch
    ]

    output = process_paths_in_batches(magika, paths, batch_size=5, max_workers=2)

    assert len(output) == 20
    result_paths = [p for p, _ in output]
    assert result_paths == paths
