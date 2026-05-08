"""Unit tests for magika.retry_magika.RetryMagika."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magika.retry import RetryExhausted, RetryPolicy
from magika.retry_magika import RetryMagika


def _mock_result(label: str = "python") -> MagicMock:
    result = MagicMock()
    result.output.ct_label = label
    return result


@pytest.fixture()
def policy() -> RetryPolicy:
    return RetryPolicy(max_attempts=3, delay_seconds=0)


@pytest.fixture()
def mock_magika() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def engine(mock_magika: MagicMock, policy: RetryPolicy) -> RetryMagika:
    return RetryMagika(magika=mock_magika, policy=policy)


# ---------------------------------------------------------------------------
# identify_bytes
# ---------------------------------------------------------------------------


def test_identify_bytes_delegates_to_inner(
    engine: RetryMagika, mock_magika: MagicMock
) -> None:
    mock_magika.identify_bytes.return_value = _mock_result("pdf")
    result = engine.identify_bytes(b"%PDF")
    mock_magika.identify_bytes.assert_called_once_with(b"%PDF")
    assert result.output.ct_label == "pdf"


def test_identify_bytes_retries_on_os_error(
    engine: RetryMagika, mock_magika: MagicMock
) -> None:
    mock_magika.identify_bytes.side_effect = [
        OSError("transient"),
        _mock_result("text"),
    ]
    result = engine.identify_bytes(b"hello")
    assert mock_magika.identify_bytes.call_count == 2
    assert result.output.ct_label == "text"


def test_identify_bytes_raises_after_exhaustion(
    engine: RetryMagika, mock_magika: MagicMock
) -> None:
    mock_magika.identify_bytes.side_effect = OSError("always fails")
    with pytest.raises(RetryExhausted):
        engine.identify_bytes(b"data")


# ---------------------------------------------------------------------------
# identify_path
# ---------------------------------------------------------------------------


def test_identify_path_delegates(engine: RetryMagika, mock_magika: MagicMock) -> None:
    p = Path("/tmp/file.py")
    mock_magika.identify_path.return_value = _mock_result("python")
    result = engine.identify_path(p)
    mock_magika.identify_path.assert_called_once_with(p)
    assert result.output.ct_label == "python"


# ---------------------------------------------------------------------------
# identify_paths
# ---------------------------------------------------------------------------


def test_identify_paths_delegates(
    engine: RetryMagika, mock_magika: MagicMock
) -> None:
    paths = [Path("/a"), Path("/b")]
    expected = [_mock_result("python"), _mock_result("json")]
    mock_magika.identify_paths.return_value = expected
    results = engine.identify_paths(paths)
    mock_magika.identify_paths.assert_called_once_with(paths)
    assert results == expected


def test_default_construction_uses_magika() -> None:
    """RetryMagika can be instantiated without arguments."""
    with patch("magika.retry_magika.Magika") as MockMagika:
        MockMagika.return_value = MagicMock()
        engine = RetryMagika()
        assert engine._policy.max_attempts >= 1
        MockMagika.assert_called_once()
