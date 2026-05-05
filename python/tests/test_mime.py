"""Tests for python/magika/mime.py."""

from __future__ import annotations

import pytest

from magika.mime import all_mime_types, label_to_mime, mime_to_labels


# ---------------------------------------------------------------------------
# label_to_mime
# ---------------------------------------------------------------------------

class TestLabelToMime:
    def test_known_label_returns_correct_mime(self):
        assert label_to_mime("pdf") == "application/pdf"

    def test_image_label(self):
        assert label_to_mime("png") == "image/png"

    def test_text_label(self):
        assert label_to_mime("python") == "text/x-python"

    def test_unknown_label_fallback_binary(self):
        assert label_to_mime("unknown_xyz") == "application/octet-stream"

    def test_unknown_label_fallback_text(self):
        assert label_to_mime("unknown_xyz", is_text=True) == "text/plain"

    def test_known_label_ignores_is_text_flag(self):
        # Even with is_text=True, a known label keeps its specific MIME type.
        assert label_to_mime("pdf", is_text=True) == "application/pdf"

    @pytest.mark.parametrize("label,expected", [
        ("json", "application/json"),
        ("html", "text/html"),
        ("zip", "application/zip"),
        ("jpeg", "image/jpeg"),
        ("yaml", "application/yaml"),
    ])
    def test_parametrized_known_labels(self, label, expected):
        assert label_to_mime(label) == expected


# ---------------------------------------------------------------------------
# mime_to_labels
# ---------------------------------------------------------------------------

class TestMimeToLabels:
    def test_returns_list_for_known_mime(self):
        labels = mime_to_labels("image/png")
        assert "png" in labels

    def test_returns_empty_for_unknown_mime(self):
        assert mime_to_labels("application/x-does-not-exist") == []

    def test_case_insensitive(self):
        assert mime_to_labels("IMAGE/PNG") == mime_to_labels("image/png")

    def test_text_plain_returns_multiple_or_one(self):
        labels = mime_to_labels("text/plain")
        # At least "text" and "ini" map to text/plain
        assert len(labels) >= 1
        assert "text" in labels

    def test_round_trip(self):
        """label -> mime -> labels should contain the original label."""
        original = "pdf"
        mime = label_to_mime(original)
        assert original in mime_to_labels(mime)


# ---------------------------------------------------------------------------
# all_mime_types
# ---------------------------------------------------------------------------

class TestAllMimeTypes:
    def test_returns_non_empty_list(self):
        mimes = all_mime_types()
        assert len(mimes) > 0

    def test_is_sorted(self):
        mimes = all_mime_types()
        assert mimes == sorted(mimes)

    def test_no_duplicates(self):
        mimes = all_mime_types()
        assert len(mimes) == len(set(mimes))

    def test_contains_common_types(self):
        mimes = all_mime_types()
        assert "application/pdf" in mimes
        assert "image/png" in mimes
        assert "text/html" in mimes
