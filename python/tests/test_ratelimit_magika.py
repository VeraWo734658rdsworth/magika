"""Unit tests for magika.ratelimit_magika."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.ratelimit import RateLimitExceeded, RateLimitPolicy
from magika.ratelimit_magika import RateLimitMagika


def _mock_result(label: str = "python") -> MagicMock:
    r = MagicMock()
    r.output.ct_label = label
    return r


@pytest.fixture()
def mock_magika():
    m = MagicMock()
    m.identify_bytes.return_value = _mock_result()
    m.identify_path.return_value = _mock_result()
    m.identify_paths.side_effect = lambda paths: [_mock_result() for _ in paths]
    return m


@pytest.fixture()
def engine(mock_magika):
    policy = RateLimitPolicy(max_calls=3, window_seconds=60.0)
    return RateLimitMagika(mock_magika, policy)


def test_identify_bytes_delegates(engine, mock_magika):
    result = engine.identify_bytes(b"hello")
    mock_magika.identify_bytes.assert_called_once_with(b"hello")
    assert result is not None


def test_identify_path_delegates(engine, mock_magika):
    p = Path("/tmp/file.py")
    engine.identify_path(p)
    mock_magika.identify_path.assert_called_once_with(p)


def test_identify_paths_delegates(engine, mock_magika):
    paths = [Path("/a"), Path("/b")]
    results = engine.identify_paths(paths)
    assert len(results) == 2
    mock_magika.identify_paths.assert_called_once_with(paths)


def test_rate_limit_exceeded_on_bytes(engine):
    engine.identify_bytes(b"a")
    engine.identify_bytes(b"b")
    engine.identify_bytes(b"c")
    with pytest.raises(RateLimitExceeded):
        engine.identify_bytes(b"d")


def test_reset_restores_capacity(engine):
    engine.identify_bytes(b"a")
    engine.identify_bytes(b"b")
    engine.identify_bytes(b"c")
    engine.reset_limit()
    engine.identify_bytes(b"d")  # should not raise


def test_limiter_property_returns_limiter(engine):
    from magika.ratelimit import RateLimiter
    assert isinstance(engine.limiter, RateLimiter)


def test_identify_paths_counts_each_path(mock_magika):
    policy = RateLimitPolicy(max_calls=2, window_seconds=60.0)
    eng = RateLimitMagika(mock_magika, policy)
    with pytest.raises(RateLimitExceeded):
        eng.identify_paths([Path("/a"), Path("/b"), Path("/c")])
