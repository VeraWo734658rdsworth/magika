"""Integration-style tests combining QuotaTracker with QuotaMagika."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from magika.quota import QuotaExceeded, QuotaPolicy, QuotaTracker
from magika.quota_magika import QuotaMagika


def _make_engine(limit: int) -> tuple[QuotaMagika, MagicMock]:
    inner = MagicMock()
    inner.identify_bytes.return_value = MagicMock()
    policy = QuotaPolicy(max_requests=limit, window_seconds=3600.0)
    return QuotaMagika(inner=inner, policy=policy), inner


def test_current_count_increments_with_calls() -> None:
    engine, _ = _make_engine(10)
    assert engine.tracker.current_count == 0
    engine.identify_bytes(b"a")
    assert engine.tracker.current_count == 1
    engine.identify_bytes(b"b")
    assert engine.tracker.current_count == 2


def test_inner_not_called_when_quota_exceeded() -> None:
    engine, inner = _make_engine(1)
    engine.identify_bytes(b"first")
    with pytest.raises(QuotaExceeded):
        engine.identify_bytes(b"second")
    assert inner.identify_bytes.call_count == 1


def test_reset_restores_full_quota() -> None:
    engine, inner = _make_engine(2)
    engine.identify_bytes(b"a")
    engine.identify_bytes(b"b")
    engine.reset_quota()
    engine.identify_bytes(b"c")
    engine.identify_bytes(b"d")
    assert inner.identify_bytes.call_count == 4


def test_quota_tracker_standalone_matches_engine_count() -> None:
    """A standalone QuotaTracker should behave identically to the one inside QuotaMagika."""
    policy = QuotaPolicy(max_requests=5, window_seconds=3600.0)
    standalone = QuotaTracker(policy=policy)
    engine, _ = _make_engine(5)

    for _ in range(4):
        standalone.check_and_record()
        engine.identify_bytes(b"x")

    assert standalone.current_count == engine.tracker.current_count


def test_policy_with_limit_one() -> None:
    engine, inner = _make_engine(1)
    engine.identify_bytes(b"only")
    with pytest.raises(QuotaExceeded) as exc_info:
        engine.identify_bytes(b"blocked")
    assert exc_info.value.limit == 1
    assert inner.identify_bytes.call_count == 1
