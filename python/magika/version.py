"""Version information and compatibility utilities for magika."""

from __future__ import annotations

import importlib.metadata
from dataclasses import dataclass
from functools import total_ordering
from typing import Tuple


@total_ordering
@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int

    def __post_init__(self) -> None:
        for part in (self.major, self.minor, self.patch):
            if part < 0:
                raise ValueError(f"Version components must be non-negative, got {part}")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._tuple() < other._tuple()

    def _tuple(self) -> Tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    def is_compatible_with(self, other: "Version") -> bool:
        """Returns True if this version is backwards-compatible with *other*.

        Compatibility is defined as sharing the same major version and having
        a minor version >= the other's minor version.
        """
        return self.major == other.major and self.minor >= other.minor

    @classmethod
    def parse(cls, version_string: str) -> "Version"
        """Parse a version string of the form 'MAJOR.MINOR.PATCH'."""
        parts = version_string.strip().split(".")
        if len(parts) != 3:
            raise ValueError(
                f"Expected version string 'MAJOR.MINOR.PATCH', got {version_string!r}"
            )
        try:
            major, minor, patch = (int(p) for p in parts)
        except ValueError:
            raise ValueError(
                f"Version components must be integers, got {version_string!r}"
            )
        return cls(major=major, minor=minor, patch=patch)


def get_package_version() -> str:
    """Return the installed package version string, or 'unknown' if unavailable."""
    try:
        return importlib.metadata.version("magika")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def get_version() -> Version:
    """Return the installed package version as a :class:`Version` object."""
    raw = get_package_version()
    if raw == "unknown":
        return Version(0, 0, 0)
    return Version.parse(raw)
