"""Unit tests for magika.budget_magika."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magika.budget import BudgetExceeded, BudgetPolicy
from magika.budget_magika import BudgetMagika


def _mock_result(label: str = "python") -> MagicMock:
    result = MagicMock()
    result.prediction.label = label
    return result


@pytest.fixture()
def policy() -> BudgetPolicy:
    return BudgetPolicy(max_bytes=200)


@pytest.fixture()
def mock_magika() -> MagicMock:
    inner = MagicMock()
    inner.identify_bytes.return_value = _mock_result()
    inner.identify_path.return_value = _mock_result()
    inner.identify_paths.return_value = [_mock_result()]
    return inner


@pytest.fixture()
def engine(mock_magika: MagicMock, policy: BudgetPolicy) -> BudgetMagika:
    return BudgetMagika(inner=mock_magika, policy=policy)


def test_identify_bytes_delegates(engine: BudgetMagika, mock_magika: MagicMock) -> None:
    data = b"hello world"
    result = engine.identify_bytes(data)
    mock_magika.identify_bytes.assert_called_once_with(data)
    assert result is not None


def test_identify_bytes_tracks_usage(engine: BudgetMagika) -> None:
    engine.identify_bytes(b"x" * 50)
    assert engine.tracker.used == 50


def test_identify_bytes_raises_when_over_budget(engine: BudgetMagika) -> None:
    engine.identify_bytes(b"x" * 150)
    with pytest.raises(BudgetExceeded):
        engine.identify_bytes(b"x" * 100)


def test_reset_budget_restores_capacity(engine: BudgetMagika) -> None:
    engine.identify_bytes(b"x" * 180)
    engine.reset_budget()
    assert engine.tracker.used == 0
    # Should not raise now
    engine.identify_bytes(b"x" * 180)


def test_identify_path_uses_file_size(engine: BudgetMagika) -> None:
    fake_path = MagicMock(spec=Path)
    fake_path.stat.return_value.st_size = 75
    engine.identify_path(fake_path)
    assert engine.tracker.used == 75


def test_identify_path_raises_when_over_budget(engine: BudgetMagika) -> None:
    fake_path = MagicMock(spec=Path)
    fake_path.stat.return_value.st_size = 250
    with pytest.raises(BudgetExceeded):
        engine.identify_path(fake_path)


def test_identify_paths_accumulates_sizes(engine: BudgetMagika, mock_magika: MagicMock) -> None:
    mock_magika.identify_path.return_value = _mock_result()
    paths = []
    for _ in range(3):
        p = MagicMock(spec=Path)
        p.stat.return_value.st_size = 30
        paths.append(p)
    results = engine.identify_paths(paths)
    assert engine.tracker.used == 90
    assert len(results) == 3
