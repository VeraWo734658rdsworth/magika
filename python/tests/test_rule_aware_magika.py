"""Tests for RuleAwareMagika."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magika.rule_aware_magika import RuleAwareMagika
from magika.rules import Rule
from magika.types import Status


def _mock_magika_result(label: str) -> MagicMock:
    result = MagicMock()
    result.prediction.ct_label = label
    result.status = Status.OK
    return result


@pytest.fixture()
def engine() -> RuleAwareMagika:
    """Return a RuleAwareMagika with the underlying Magika model mocked out."""
    with patch("magika.rule_aware_magika.Magika") as MockMagika:
        instance = MockMagika.return_value
        instance.identify_path.return_value = _mock_magika_result("txt")
        instance.identify_bytes.return_value = _mock_magika_result("txt")
        yield RuleAwareMagika.__new__(RuleAwareMagika)
        # manually init so the mock is already in place


# ---------------------------------------------------------------------------
# identify_bytes
# ---------------------------------------------------------------------------

class TestIdentifyBytes:
    def test_rule_overrides_model_for_pdf(self):
        with patch("magika.rule_aware_magika.Magika"):
            ram = RuleAwareMagika()
            ram._magika = MagicMock()
            result = ram.identify_bytes(b"%PDF-1.4 content")
        assert result.prediction.ct_label == "pdf"
        ram._magika.identify_bytes.assert_not_called()

    def test_falls_through_to_model_when_no_rule(self):
        mock_result = _mock_magika_result("txt")
        with patch("magika.rule_aware_magika.Magika"):
            ram = RuleAwareMagika()
            ram._magika = MagicMock()
            ram._magika.identify_bytes.return_value = mock_result
            result = ram.identify_bytes(b"plain text content")
        assert result.prediction.ct_label == "txt"
        ram._magika.identify_bytes.assert_called_once()

    def test_custom_rule_respected(self):
        custom = Rule(label="custom_type", description="test", magic_bytes=b"MAGIC")
        with patch("magika.rule_aware_magika.Magika"):
            ram = RuleAwareMagika(extra_rules=[custom])
            ram._magika = MagicMock()
            result = ram.identify_bytes(b"MAGICdata")
        assert result.prediction.ct_label == "custom_type"

    def test_rule_result_has_full_confidence(self):
        with patch("magika.rule_aware_magika.Magika"):
            ram = RuleAwareMagika()
            result = ram.identify_bytes(b"%PDF-1.0")
        assert result.prediction.score == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# identify_path
# ---------------------------------------------------------------------------

class TestIdentifyPath:
    def test_dockerfile_matched_by_name(self, tmp_path):
        df = tmp_path / "Dockerfile"
        df.write_bytes(b"FROM ubuntu:22.04")
        with patch("magika.rule_aware_magika.Magika"):
            ram = RuleAwareMagika()
            ram._magika = MagicMock()
            result = ram.identify_path(df)
        assert result.prediction.ct_label == "dockerfile"

    def test_identify_paths_delegates(self, tmp_path):
        f1 = tmp_path / "a.txt"
        f1.write_bytes(b"hello")
        f2 = tmp_path / "b.pdf"
        f2.write_bytes(b"%PDF-1.4")
        with patch("magika.rule_aware_magika.Magika"):
            ram = RuleAwareMagika()
            mock_res = _mock_magika_result("txt")
            ram._magika = MagicMock()
            ram._magika.identify_path.return_value = mock_res
            results = ram.identify_paths([f1, f2])
        assert len(results) == 2
        assert results[1].prediction.ct_label == "pdf"
