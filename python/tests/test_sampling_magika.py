"""Unit tests for magika.sampling_magika.SamplingMagika."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from magika.prediction import MagikaResult
from magika.sampling import SamplingPolicy
from magika.sampling_magika import SamplingMagika


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_result(label: str = "text") -> MagikaResult:
    r = MagicMock(spec=MagikaResult)
    r.label = label
    return r


@pytest.fixture()
def mock_magika():
    m = MagicMock()
    m.identify_bytes.return_value = _mock_result("pdf")
    m.identify_path.return_value = _mock_result("pdf")
    m.identify_paths.return_value = [_mock_result("pdf")]
    return m


@pytest.fixture()
def engine(mock_magika):
    policy = SamplingPolicy(max_samples=3, seed=0)
    return SamplingMagika(mock_magika, policy)


# ---------------------------------------------------------------------------
# Single-item delegation
# ---------------------------------------------------------------------------

def test_identify_bytes_delegates_directly(engine, mock_magika):
    engine.identify_bytes(b"hello")
    mock_magika.identify_bytes.assert_called_once_with(b"hello")


def test_identify_path_delegates_directly(engine, mock_magika):
    p = Path("/tmp/x.pdf")
    engine.identify_path(p)
    mock_magika.identify_path.assert_called_once_with(p)


# ---------------------------------------------------------------------------
# identify_paths sampling
# ---------------------------------------------------------------------------

def test_identify_paths_passes_all_when_under_limit(mock_magika):
    policy = SamplingPolicy(max_samples=10, seed=0)
    eng = SamplingMagika(mock_magika, policy)
    paths = [Path(f"/tmp/{i}.bin") for i in range(5)]
    mock_magika.identify_paths.return_value = [_mock_result() for _ in paths]
    eng.identify_paths(paths)
    called_paths = mock_magika.identify_paths.call_args[0][0]
    assert len(called_paths) == 5


def test_identify_paths_samples_when_over_limit(mock_magika):
    policy = SamplingPolicy(max_samples=3, seed=1)
    eng = SamplingMagika(mock_magika, policy)
    paths = [Path(f"/tmp/{i}.bin") for i in range(20)]
    mock_magika.identify_paths.return_value = [_mock_result() for _ in range(3)]
    eng.identify_paths(paths)
    called_paths = mock_magika.identify_paths.call_args[0][0]
    assert len(called_paths) == 3


# ---------------------------------------------------------------------------
# identify_bytes_batch sampling
# ---------------------------------------------------------------------------

def test_identify_bytes_batch_samples_inputs(mock_magika):
    policy = SamplingPolicy(max_samples=2, seed=42)
    eng = SamplingMagika(mock_magika, policy)
    inputs = [bytes([i]) * 8 for i in range(10)]
    results = eng.identify_bytes_batch(inputs)
    assert len(results) == 2
    assert mock_magika.identify_bytes.call_count == 2


def test_policy_property_returns_policy(engine):
    assert engine.policy.max_samples == 3
