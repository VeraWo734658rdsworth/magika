"""Unit tests for magika.ratelimit."""
from __future__ import annotations

import time
import pytest

from magika.ratelimit import RateLimitExceeded, RateLimitPolicy, RateLimiter


def test_default_policy_is_valid():
    p = RateLimitPolicy()
    assert p.max_calls > 0
    assert p.window_seconds > 0


def test_policy_rejects_zero_calls():
    with pytest.raises(ValueError):
        RateLimitPolicy(max_calls=0)


def test_policy_rejects_negative_calls():
    with pytest.raises(ValueError):
        RateLimitPolicy(max_calls=-1)


def test_policy_rejects_zero_window():
    with pytest.raises(ValueError):
        RateLimitPolicy(window_seconds=0.0)


def test_policy_rejects_negative_window():
    with pytest.raises(ValueError):
        RateLimitPolicy(window_seconds=-5.0)


def test_single_call_allowed():
    limiter = RateLimiter(RateLimitPolicy(max_calls=1, window_seconds=1.0))
    limiter.check_and_record()  # should not raise


def test_exceeding_limit_raises():
    limiter = RateLimiter(RateLimitPolicy(max_calls=2, window_seconds=60.0))
    limiter.check_and_record()
    limiter.check_and_record()
    with pytest.raises(RateLimitExceeded):
        limiter.check_and_record()


def test_current_count_starts_at_zero():
    limiter = RateLimiter(RateLimitPolicy())
    assert limiter.current_count() == 0


def test_current_count_increments():
    limiter = RateLimiter(RateLimitPolicy(max_calls=10, window_seconds=60.0))
    limiter.check_and_record()
    limiter.check_and_record()
    assert limiter.current_count() == 2


def test_reset_clears_count():
    limiter = RateLimiter(RateLimitPolicy(max_calls=5, window_seconds=60.0))
    limiter.check_and_record()
    limiter.check_and_record()
    limiter.reset()
    assert limiter.current_count() == 0


def test_exception_carries_limit_and_window():
    exc = RateLimitExceeded(limit=3, window=0.5)
    assert exc.limit == 3
    assert exc.window == 0.5
    assert "3" in str(exc)
    assert "0.5" in str(exc)


def test_old_calls_evicted_after_window(monkeypatch):
    """Calls outside the window should not count toward the limit."""
    clock = [0.0]
    monkeypatch.setattr(time, "monotonic", lambda: clock[0])

    limiter = RateLimiter(RateLimitPolicy(max_calls=1, window_seconds=1.0))
    limiter.check_and_record()   # t=0
    clock[0] = 1.1               # advance past the window
    limiter.check_and_record()   # should succeed — old entry evicted
