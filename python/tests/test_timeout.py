"""Tests for magika.timeout and TimeoutMagika."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.timeout import TimeoutExceeded, TimeoutPolicy, _run_with_timeout
from magika.timeout_magika import TimeoutMagika


# ---------------------------------------------------------------------------
# TimeoutPolicy
# ---------------------------------------------------------------------------

def test_default_policy_is_valid():
    p = TimeoutPolicy()
    assert p.seconds > 0


def test_policy_rejects_zero_seconds():
    with pytest.raises(ValueError):
        TimeoutPolicy(seconds=0)


def test_policy_rejects_negative_seconds():
    with pytest.raises(ValueError):
        TimeoutPolicy(seconds=-1.0)


def test_policy_accepts_custom_seconds():
    p = TimeoutPolicy(seconds=5.0)
    assert p.seconds == 5.0


# ---------------------------------------------------------------------------
# _run_with_timeout
# ---------------------------------------------------------------------------

def test_fast_function_returns_result():
    result = _run_with_timeout(lambda: 42, TimeoutPolicy(seconds=5.0))
    assert result == 42


def test_slow_function_raises_timeout():
    with pytest.raises(TimeoutExceeded) as exc_info:
        _run_with_timeout(lambda: time.sleep(10), TimeoutPolicy(seconds=0.05))
    assert exc_info.value.seconds == pytest.approx(0.05)


def test_exception_in_function_propagates():
    def _boom():
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        _run_with_timeout(_boom, TimeoutPolicy(seconds=5.0))


# ---------------------------------------------------------------------------
# TimeoutMagika
# ---------------------------------------------------------------------------

@pytest.fixture()
def _mock_result():
    r = MagicMock()
    r.output.label = "python"
    return r


@pytest.fixture()
def mock_magika(_mock_result):
    m = MagicMock()
    m.identify_bytes.return_value = _mock_result
    m.identify_path.return_value = _mock_result
    m.identify_paths.return_value = [_mock_result]
    return m


@pytest.fixture()
def engine(mock_magika):
    return TimeoutMagika(mock_magika, TimeoutPolicy(seconds=5.0))


def test_identify_bytes_delegates(engine, mock_magika, _mock_result):
    assert engine.identify_bytes(b"data") is _mock_result
    mock_magika.identify_bytes.assert_called_once_with(b"data")


def test_identify_path_delegates(engine, mock_magika, _mock_result):
    p = Path("/tmp/file.py")
    assert engine.identify_path(p) is _mock_result
    mock_magika.identify_path.assert_called_once_with(p)


def test_identify_paths_delegates(engine, mock_magika, _mock_result):
    paths = [Path("/tmp/a.py"), Path("/tmp/b.py")]
    results = engine.identify_paths(paths)
    assert results == [_mock_result]
    mock_magika.identify_paths.assert_called_once_with(paths)


def test_slow_identify_bytes_raises_timeout(mock_magika):
    def _slow(_):
        time.sleep(10)

    mock_magika.identify_bytes.side_effect = _slow
    engine = TimeoutMagika(mock_magika, TimeoutPolicy(seconds=0.05))
    with pytest.raises(TimeoutExceeded):
        engine.identify_bytes(b"data")
