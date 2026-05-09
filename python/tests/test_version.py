"""Tests for python/magika/version.py."""

from __future__ import annotations

import pytest

from magika.version import Version, get_package_version, get_version


class TestVersionParse:
    def test_valid_string(self):
        v = Version.parse("1.2.3")
        assert v == Version(1, 2, 3)

    def test_leading_trailing_whitespace(self):
        v = Version.parse("  0.1.0  ")
        assert v == Version(0, 1, 0)

    def test_too_few_parts_raises(self):
        with pytest.raises(ValueError, match="MAJOR.MINOR.PATCH"):
            Version.parse("1.2")

    def test_too_many_parts_raises(self):
        with pytest.raises(ValueError, match="MAJOR.MINOR.PATCH"):
            Version.parse("1.2.3.4")

    def test_non_integer_raises(self):
        with pytest.raises(ValueError, match="integers"):
            Version.parse("1.a.3")


class TestVersionStr:
    def test_str_format(self):
        assert str(Version(2, 10, 0)) == "2.10.0"

    def test_str_zeros(self):
        assert str(Version(0, 0, 0)) == "0.0.0"


class TestVersionOrdering:
    def test_equal(self):
        assert Version(1, 2, 3) == Version(1, 2, 3)

    def test_less_than_by_major(self):
        assert Version(1, 9, 9) < Version(2, 0, 0)

    def test_less_than_by_minor(self):
        assert Version(1, 2, 9) < Version(1, 3, 0)

    def test_less_than_by_patch(self):
        assert Version(1, 2, 3) < Version(1, 2, 4)

    def test_greater_than(self):
        assert Version(2, 0, 0) > Version(1, 9, 9)


class TestVersionNegativeRaises:
    def test_negative_major_raises(self):
        with pytest.raises(ValueError):
            Version(-1, 0, 0)

    def test_negative_patch_raises(self):
        with pytest.raises(ValueError):
            Version(1, 0, -1)


class TestCompatibility:
    def test_same_version_is_compatible(self):
        v = Version(1, 2, 3)
        assert v.is_compatible_with(Version(1, 2, 3))

    def test_higher_minor_is_compatible(self):
        assert Version(1, 3, 0).is_compatible_with(Version(1, 2, 0))

    def test_lower_minor_is_not_compatible(self):
        assert not Version(1, 1, 0).is_compatible_with(Version(1, 2, 0))

    def test_different_major_is_not_compatible(self):
        assert not Version(2, 0, 0).is_compatible_with(Version(1, 9, 0))


class TestGetPackageVersion:
    def test_returns_string(self):
        result = get_package_version()
        assert isinstance(result, str)
        assert len(result) > 0


class TestGetVersion:
    def test_returns_version_instance(self):
        v = get_version()
        assert isinstance(v, Version)

    def test_unknown_package_returns_zero_version(self, monkeypatch):
        import magika.version as version_mod
        monkeypatch.setattr(version_mod, "get_package_version", lambda: "unknown")
        v = get_version()
        assert v == Version(0, 0, 0)
