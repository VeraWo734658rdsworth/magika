"""Unit tests for magika.quota."""
from __future__ import annotations

import time

import pytest

from magika.quota import QuotaExceeded, QuotaPolicy, QuotaTracker


# ---------------------------------------------------------------------------
# QuotaPolicy validation
# ---------------------------------------------------------------------------

def test_default_policy_is_valid() -> None:
    p = QuotaPolicy()
    assert p.max_requests >= 1
    assert p.window_seconds > 0


def test_policy_rejects_zero_requests() -> None:
    with pytest.raises(ValueError, match="max_requests"):
        QuotaPolicy(max_requests=0)


def test_policy_rejects_negative_window() -> None:
    with pytest.raises(ValueError, match="window_seconds"):
        QuotaPolicy(window_seconds=-1.0)


def test_policy_rejects_zero_window() -> None:
    with pytest.raises(ValueError, match="window_seconds"):
        QuotaPolicy(window_seconds=0.0)


# ---------------------------------------------------------------------------
# QuotaTracker behaviour
# ---------------------------------------------------------------------------

def test_single_request_allowed() -> None:
    tracker = QuotaTracker(policy=QuotaPolicy(max_requests=5, window_seconds=60))
    tracker.check_and_record()  # should not raise
    assert tracker.current_count == 1


def test_requests_up_to_limit_allowed() -> None:
    limit = 3
    tracker = QuotaTracker(policy=QuotaPolicy(max_requests=limit, window_seconds=60))
    for _ in range(limit):
        tracker.check_and_record()
    assert tracker.current_count == limit


def test_exceeding_limit_raises() -> None:
    tracker = QuotaTracker(policy=QuotaPolicy(max_requests=2, window_seconds=60))
    tracker.check_and_record()
    tracker.check_and_record()
    with pytest.raises(QuotaExceeded):
        tracker.check_and_record()


def test_quota_exceeded_carries_metadata() -> None:
    policy = QuotaPolicy(max_requests=1, window_seconds=30.0)
    tracker = QuotaTracker(policy=policy)
    tracker.check_and_record()
    with pytest.raises(QuotaExceeded) as exc_info:
        tracker.check_and_record()
    err = exc_info.value
    assert err.limit == 1
    assert err.window == 30.0


def test_reset_clears_counter() -> None:
    tracker = QuotaTracker(policy=QuotaPolicy(max_requests=1, window_seconds=60))
    tracker.check_and_record()
    tracker.reset()
    assert tracker.current_count == 0
    tracker.check_and_record()  # should not raise after reset


def test_old_requests_evicted_after_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """Timestamps older than the window should not count toward the quota."""
    calls: list[float] = []

    base = 1_000_000.0
    calls.append(base)
    calls.append(base + 61.0)  # second call is outside a 60 s window

    monkeypatch.setattr(time, "monotonic", lambda: calls.pop(0))

    policy = QuotaPolicy(max_requests=1, window_seconds=60.0)
    tracker = QuotaTracker(policy=policy)
    tracker.check_and_record()  # recorded at base
    # After the window advances, the old timestamp is evicted
    tracker.check_and_record()  # recorded at base+61 — should succeed
