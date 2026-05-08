"""Unit tests for magika.quota_magika.QuotaMagika."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magika.quota import QuotaExceeded, QuotaPolicy
from magika.quota_magika import QuotaMagika


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _mock_result() -> MagicMock:
    result = MagicMock()
    result.prediction.label = "python"
    return result


@pytest.fixture()
def mock_magika() -> MagicMock:
    m = MagicMock()
    m.identify_bytes.return_value = _mock_result()
    m.identify_path.return_value = _mock_result()
    m.identify_paths.return_value = [_mock_result()]
    return m


@pytest.fixture()
def engine(mock_magika: MagicMock) -> QuotaMagika:
    policy = QuotaPolicy(max_requests=3, window_seconds=60.0)
    return QuotaMagika(inner=mock_magika, policy=policy)


# ---------------------------------------------------------------------------
# Delegation tests
# ---------------------------------------------------------------------------

def test_identify_bytes_delegates(engine: QuotaMagika, mock_magika: MagicMock) -> None:
    result = engine.identify_bytes(b"hello")
    mock_magika.identify_bytes.assert_called_once_with(b"hello")
    assert result is not None


def test_identify_path_delegates(engine: QuotaMagika, mock_magika: MagicMock) -> None:
    p = Path("sample.py")
    engine.identify_path(p)
    mock_magika.identify_path.assert_called_once_with(p)


def test_identify_paths_delegates(engine: QuotaMagika, mock_magika: MagicMock) -> None:
    paths = [Path("a.py"), Path("b.py")]
    results = engine.identify_paths(paths)
    mock_magika.identify_paths.assert_called_once_with(paths)
    assert isinstance(results, list)


# ---------------------------------------------------------------------------
# Quota enforcement
# ---------------------------------------------------------------------------

def test_quota_enforced_on_identify_bytes(engine: QuotaMagika) -> None:
    for _ in range(3):
        engine.identify_bytes(b"data")
    with pytest.raises(QuotaExceeded):
        engine.identify_bytes(b"data")


def test_quota_enforced_across_methods(engine: QuotaMagika) -> None:
    engine.identify_bytes(b"x")
    engine.identify_path(Path("f.py"))
    engine.identify_paths([Path("g.py")])
    with pytest.raises(QuotaExceeded):
        engine.identify_bytes(b"x")


def test_reset_quota_allows_further_calls(engine: QuotaMagika) -> None:
    for _ in range(3):
        engine.identify_bytes(b"x")
    engine.reset_quota()
    engine.identify_bytes(b"x")  # should not raise


def test_tracker_exposed(engine: QuotaMagika) -> None:
    assert engine.tracker is not None
    assert engine.tracker.current_count == 0
