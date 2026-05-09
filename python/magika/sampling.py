"""Sampling utilities for magika — randomly select a subset of paths or bytes inputs."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence


class SamplingError(ValueError):
    """Raised when sampling parameters are invalid."""


@dataclass
class SamplingPolicy:
    """Controls how inputs are sampled before identification."""

    max_samples: int
    seed: Optional[int] = None
    shuffle: bool = True

    def __post_init__(self) -> None:
        if self.max_samples < 1:
            raise SamplingError("max_samples must be at least 1")


def sample_paths(
    paths: Sequence[Path],
    policy: SamplingPolicy,
) -> List[Path]:
    """Return up to *policy.max_samples* paths, optionally shuffled."""
    paths = list(paths)
    if len(paths) <= policy.max_samples:
        if policy.shuffle:
            rng = random.Random(policy.seed)
            rng.shuffle(paths)
        return paths
    rng = random.Random(policy.seed)
    return rng.sample(paths, policy.max_samples)


def sample_bytes_inputs(
    inputs: Sequence[bytes],
    policy: SamplingPolicy,
) -> List[bytes]:
    """Return up to *policy.max_samples* byte strings, optionally shuffled."""
    inputs = list(inputs)
    if len(inputs) <= policy.max_samples:
        if policy.shuffle:
            rng = random.Random(policy.seed)
            rng.shuffle(inputs)
        return inputs
    rng = random.Random(policy.seed)
    return rng.sample(inputs, policy.max_samples)
