"""Tests for python/magika/watch.py."""
from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from magika.watch import WatchError, WatchPolicy, WatchSession, watch


# ---------------------------------------------------------------------------
# WatchPolicy
# ---------------------------------------------------------------------------

class TestWatchPolicy:
    def test_default_policy_is_valid(self):
        p = WatchPolicy()
        assert p.interval_seconds == 2.0
        assert p.recursive is False
        assert p.extensions is None

    def test_zero_interval_raises(self):
        with pytest.raises(WatchError):
            WatchPolicy(interval_seconds=0)

    def test_negative_interval_raises(self):
        with pytest.raises(WatchError):
            WatchPolicy(interval_seconds=-1.0)

    def test_extensions_normalised_to_lowercase_no_dot(self):
        p = WatchPolicy(extensions=[".PY", "TXT"])
        assert p.extensions == ["py", "txt"]

    def test_empty_extension_raises(self):
        with pytest.raises(WatchError):
            WatchPolicy(extensions=[""])

    def test_matches_returns_true_for_allowed_extension(self):
        p = WatchPolicy(extensions=["py"])
        assert p.matches(Path("script.py")) is True

    def test_matches_returns_false_for_disallowed_extension(self):
        p = WatchPolicy(extensions=["py"])
        assert p.matches(Path("image.png")) is False

    def test_matches_none_extensions_always_true(self):
        p = WatchPolicy(extensions=None)
        assert p.matches(Path("anything.xyz")) is True


# ---------------------------------------------------------------------------
# WatchSession
# ---------------------------------------------------------------------------

class TestWatchSession:
    def test_first_snapshot_returns_all_files(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        session = WatchSession()
        policy = WatchPolicy(interval_seconds=1)
        new = session.snapshot(tmp_path, policy)
        assert len(new) == 2
        assert session.seen_count == 2

    def test_second_snapshot_returns_only_new_files(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        session = WatchSession()
        policy = WatchPolicy(interval_seconds=1)
        session.snapshot(tmp_path, policy)  # consume existing
        (tmp_path / "b.txt").write_text("b")
        new = session.snapshot(tmp_path, policy)
        assert [p.name for p in new] == ["b.txt"]

    def test_extension_filter_applied(self, tmp_path):
        (tmp_path / "script.py").write_text("")
        (tmp_path / "image.png").write_text("")
        session = WatchSession()
        policy = WatchPolicy(interval_seconds=1, extensions=["py"])
        new = session.snapshot(tmp_path, policy)
        assert all(p.suffix == ".py" for p in new)
        assert len(new) == 1


# ---------------------------------------------------------------------------
# watch()
# ---------------------------------------------------------------------------

def test_watch_raises_for_non_directory(tmp_path):
    fake = tmp_path / "not_a_dir"
    with pytest.raises(WatchError):
        watch(fake, WatchPolicy(), callback=lambda paths: None, max_iterations=1,
              _sleep=lambda _: None)


def test_watch_calls_callback_with_new_files(tmp_path):
    (tmp_path / "file.txt").write_text("hello")
    collected: list = []
    watch(
        tmp_path,
        WatchPolicy(interval_seconds=0.01),
        callback=lambda paths: collected.extend(paths),
        max_iterations=1,
        _sleep=lambda _: None,
    )
    assert len(collected) == 1


def test_watch_respects_max_iterations(tmp_path):
    sleep_mock = MagicMock()
    watch(
        tmp_path,
        WatchPolicy(interval_seconds=0.01),
        callback=lambda _: None,
        max_iterations=3,
        _sleep=sleep_mock,
    )
    assert sleep_mock.call_count == 3
