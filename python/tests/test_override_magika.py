"""Tests for OverrideMagika — verifies override short-circuit behaviour."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from magika.override import LabelOverride, OverrideEngine
from magika.override_magika import OverrideMagika
from magika.types import Status


def _mock_result(label: str = "unknown") -> MagicMock:
    result = MagicMock()
    result.prediction.label = label
    result.status = Status.OK
    return result


@pytest.fixture()
def engine() -> OverrideEngine:
    return OverrideEngine([
        LabelOverride(extension="rs", label="rust"),
        LabelOverride(mime="application/pdf", label="pdf"),
    ])


class TestOverrideMagika:
    def test_override_applied_for_matching_extension(self, engine: OverrideEngine):
        with patch("magika.override_magika.Magika") as MockMagika:
            om = OverrideMagika(engine=engine)
            result = om.identify_path(Path("main.rs"))
        MockMagika.return_value.identify_path.assert_not_called()
        assert result.prediction.label == "rust"

    def test_model_called_when_no_override(self, engine: OverrideEngine):
        with patch("magika.override_magika.Magika") as MockMagika:
            mock_instance = MockMagika.return_value
            mock_instance.identify_path.return_value = _mock_result("python")
            om = OverrideMagika(engine=engine)
            result = om.identify_path(Path("script.py"))
        mock_instance.identify_path.assert_called_once_with(Path("script.py"))
        assert result.prediction.label == "python"

    def test_identify_paths_applies_overrides(self, engine: OverrideEngine):
        paths = [Path("main.rs"), Path("script.py")]
        with patch("magika.override_magika.Magika") as MockMagika:
            mock_instance = MockMagika.return_value
            mock_instance.identify_path.return_value = _mock_result("python")
            om = OverrideMagika(engine=engine)
            results = om.identify_paths(paths)
        assert results[0].prediction.label == "rust"
        assert results[1].prediction.label == "python"
        mock_instance.identify_path.assert_called_once_with(Path("script.py"))

    def test_identify_bytes_bypasses_override(self, engine: OverrideEngine):
        """identify_bytes has no path, so override cannot apply."""
        with patch("magika.override_magika.Magika") as MockMagika:
            mock_instance = MockMagika.return_value
            mock_instance.identify_bytes.return_value = _mock_result("pdf")
            om = OverrideMagika(engine=engine)
            result = om.identify_bytes(b"%PDF-1.4")
        mock_instance.identify_bytes.assert_called_once_with(b"%PDF-1.4")
        assert result.prediction.label == "pdf"

    def test_empty_engine_never_overrides(self):
        with patch("magika.override_magika.Magika") as MockMagika:
            mock_instance = MockMagika.return_value
            mock_instance.identify_path.return_value = _mock_result("c")
            om = OverrideMagika(engine=OverrideEngine())
            result = om.identify_path(Path("main.c"))
        mock_instance.identify_path.assert_called_once()
        assert result.prediction.label == "c"
