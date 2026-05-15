"""Unit tests for magika.budget."""
from __future__ import annotations

import pytest

from magika.budget import BudgetExceeded, BudgetPolicy, BudgetTracker


def test_default_policy_is_valid() -> None:
    policy = BudgetPolicy(max_bytes=1024)
    assert policy.max_bytes == 1024
    assert policy.reset_on_exhaustion is False


def test_policy_rejects_zero_bytes() -> None:
    with pytest.raises(ValueError):
        BudgetPolicy(max_bytes=0)


def test_policy_rejects_negative_bytes() -> None:
    with pytest.raises(ValueError):
        BudgetPolicy(max_bytes=-1)


def test_single_consume_allowed() -> None:
    tracker = BudgetTracker(policy=BudgetPolicy(max_bytes=100))
    tracker.consume(50)
    assert tracker.used == 50
    assert tracker.remaining == 50


def test_consume_exact_limit_allowed() -> None:
    tracker = BudgetTracker(policy=BudgetPolicy(max_bytes=100))
    tracker.consume(100)
    assert tracker.used == 100
    assert tracker.remaining == 0


def test_consume_over_limit_raises() -> None:
    tracker = BudgetTracker(policy=BudgetPolicy(max_bytes=100))
    tracker.consume(80)
    with pytest.raises(BudgetExceeded) as exc_info:
        tracker.consume(30)
    assert exc_info.value.limit == 100
    assert exc_info.value.used == 110


def test_reset_restores_full_budget() -> None:
    tracker = BudgetTracker(policy=BudgetPolicy(max_bytes=100))
    tracker.consume(90)
    tracker.reset()
    assert tracker.used == 0
    assert tracker.remaining == 100


def test_reset_on_exhaustion_resets_then_raises() -> None:
    policy = BudgetPolicy(max_bytes=50, reset_on_exhaustion=True)
    tracker = BudgetTracker(policy=policy)
    tracker.consume(40)
    with pytest.raises(BudgetExceeded):
        tracker.consume(20)
    # After exhaustion reset, counter should be back to zero
    assert tracker.used == 0


def test_consume_negative_raises() -> None:
    tracker = BudgetTracker(policy=BudgetPolicy(max_bytes=100))
    with pytest.raises(ValueError):
        tracker.consume(-1)


def test_consume_zero_is_noop() -> None:
    tracker = BudgetTracker(policy=BudgetPolicy(max_bytes=100))
    tracker.consume(0)
    assert tracker.used == 0


def test_budget_exceeded_message_contains_values() -> None:
    exc = BudgetExceeded(used=200, limit=100)
    assert "200" in str(exc)
    assert "100" in str(exc)
