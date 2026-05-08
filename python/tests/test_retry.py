"""Unit tests for magika.retry."""

from __future__ import annotations

import pytest

from magika.retry import RetryExhausted, RetryPolicy, with_retry


# ---------------------------------------------------------------------------
# RetryPolicy validation
# ---------------------------------------------------------------------------


def test_default_policy_has_sensible_values() -> None:
    p = RetryPolicy()
    assert p.max_attempts >= 1
    assert p.delay_seconds >= 0
    assert p.backoff_factor >= 1.0


def test_policy_rejects_zero_attempts() -> None:
    with pytest.raises(ValueError, match="max_attempts"):
        RetryPolicy(max_attempts=0)


def test_policy_rejects_negative_delay() -> None:
    with pytest.raises(ValueError, match="delay_seconds"):
        RetryPolicy(delay_seconds=-0.1)


def test_policy_rejects_backoff_below_one() -> None:
    with pytest.raises(ValueError, match="backoff_factor"):
        RetryPolicy(backoff_factor=0.5)


# ---------------------------------------------------------------------------
# with_retry success paths
# ---------------------------------------------------------------------------


def test_success_on_first_attempt() -> None:
    calls: list[int] = []

    def fn() -> str:
        calls.append(1)
        return "ok"

    result = with_retry(fn, RetryPolicy(max_attempts=3, delay_seconds=0))
    assert result == "ok"
    assert len(calls) == 1


def test_success_after_one_failure() -> None:
    attempts: list[int] = []

    def fn() -> str:
        attempts.append(1)
        if len(attempts) < 2:
            raise OSError("transient")
        return "recovered"

    result = with_retry(fn, RetryPolicy(max_attempts=3, delay_seconds=0))
    assert result == "recovered"
    assert len(attempts) == 2


# ---------------------------------------------------------------------------
# with_retry exhaustion
# ---------------------------------------------------------------------------


def test_raises_retry_exhausted_after_all_attempts() -> None:
    policy = RetryPolicy(max_attempts=3, delay_seconds=0)

    def always_fail() -> None:
        raise OSError("boom")

    with pytest.raises(RetryExhausted) as exc_info:
        with_retry(always_fail, policy)

    assert exc_info.value.attempts == 3
    assert isinstance(exc_info.value.last_error, OSError)


def test_non_retryable_exception_propagates_immediately() -> None:
    policy = RetryPolicy(max_attempts=5, delay_seconds=0, exceptions=(OSError,))
    calls: list[int] = []

    def fn() -> None:
        calls.append(1)
        raise ValueError("not retryable")

    with pytest.raises(ValueError, match="not retryable"):
        with_retry(fn, policy)

    assert len(calls) == 1


def test_retry_exhausted_str_contains_attempt_count() -> None:
    exc = RetryExhausted(4, OSError("disk error"))
    assert "4" in str(exc)
