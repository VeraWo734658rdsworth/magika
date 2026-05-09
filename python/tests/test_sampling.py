"""Unit tests for magika.sampling."""
from __future__ import annotations

from pathlib import Path

import pytest

from magika.sampling import SamplingError, SamplingPolicy, sample_bytes_inputs, sample_paths


# ---------------------------------------------------------------------------
# SamplingPolicy validation
# ---------------------------------------------------------------------------

def test_policy_accepts_valid_params():
    p = SamplingPolicy(max_samples=10, seed=42)
    assert p.max_samples == 10
    assert p.seed == 42


def test_policy_rejects_zero_max_samples():
    with pytest.raises(SamplingError):
        SamplingPolicy(max_samples=0)


def test_policy_rejects_negative_max_samples():
    with pytest.raises(SamplingError):
        SamplingPolicy(max_samples=-5)


# ---------------------------------------------------------------------------
# sample_paths
# ---------------------------------------------------------------------------

def _paths(n: int):
    return [Path(f"/tmp/file_{i}.bin") for i in range(n)]


def test_sample_paths_returns_all_when_under_limit():
    paths = _paths(5)
    result = sample_paths(paths, SamplingPolicy(max_samples=10, seed=0))
    assert len(result) == 5


def test_sample_paths_truncates_to_max():
    paths = _paths(20)
    result = sample_paths(paths, SamplingPolicy(max_samples=7, seed=1))
    assert len(result) == 7


def test_sample_paths_deterministic_with_seed():
    paths = _paths(50)
    policy = SamplingPolicy(max_samples=10, seed=99)
    r1 = sample_paths(paths, policy)
    r2 = sample_paths(paths, policy)
    assert r1 == r2


def test_sample_paths_different_seeds_differ():
    paths = _paths(50)
    r1 = sample_paths(paths, SamplingPolicy(max_samples=10, seed=1))
    r2 = sample_paths(paths, SamplingPolicy(max_samples=10, seed=2))
    # With 50 items and seed difference this should virtually always differ
    assert r1 != r2


def test_sample_paths_shuffle_false_preserves_order_when_under_limit():
    paths = _paths(5)
    result = sample_paths(paths, SamplingPolicy(max_samples=10, shuffle=False))
    assert result == paths


# ---------------------------------------------------------------------------
# sample_bytes_inputs
# ---------------------------------------------------------------------------

def test_sample_bytes_returns_all_when_under_limit():
    inputs = [bytes([i]) * 4 for i in range(8)]
    result = sample_bytes_inputs(inputs, SamplingPolicy(max_samples=20, seed=0))
    assert len(result) == 8


def test_sample_bytes_truncates_to_max():
    inputs = [bytes([i]) for i in range(30)]
    result = sample_bytes_inputs(inputs, SamplingPolicy(max_samples=5, seed=7))
    assert len(result) == 5


def test_sample_bytes_deterministic_with_seed():
    inputs = [bytes([i]) * 10 for i in range(40)]
    policy = SamplingPolicy(max_samples=8, seed=55)
    assert sample_bytes_inputs(inputs, policy) == sample_bytes_inputs(inputs, policy)
