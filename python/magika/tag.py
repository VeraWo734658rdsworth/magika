"""Tag-based annotation for Magika results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Iterable, Iterator


class TagError(ValueError):
    """Raised when a tag value is invalid."""


@dataclass(frozen=True)
class Tag:
    """A single immutable tag string."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise TagError("Tag value must be a non-empty, non-whitespace string.")
        if self.value != self.value.strip():
            raise TagError("Tag value must not have leading or trailing whitespace.")

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Tag({self.value!r})"


@dataclass
class TagSet:
    """A mutable collection of unique tags associated with a result."""

    _tags: set[Tag] = field(default_factory=set, init=False)

    def add(self, tag: str | Tag) -> None:
        """Add a tag to the set."""
        if isinstance(tag, str):
            tag = Tag(tag)
        self._tags.add(tag)

    def remove(self, tag: str | Tag) -> None:
        """Remove a tag; silently ignores missing tags."""
        if isinstance(tag, str):
            tag = Tag(tag)
        self._tags.discard(tag)

    def has(self, tag: str | Tag) -> bool:
        """Return True if the tag is present."""
        if isinstance(tag, str):
            tag = Tag(tag)
        return tag in self._tags

    def all(self) -> FrozenSet[Tag]:
        """Return an immutable snapshot of all tags."""
        return frozenset(self._tags)

    def filter(self, prefix: str) -> list[Tag]:
        """Return tags whose value starts with *prefix*."""
        return sorted(
            (t for t in self._tags if t.value.startswith(prefix)),
            key=lambda t: t.value,
        )

    def __len__(self) -> int:
        return len(self._tags)

    def __iter__(self) -> Iterator[Tag]:
        return iter(sorted(self._tags, key=lambda t: t.value))

    def __repr__(self) -> str:
        tags = ", ".join(str(t) for t in self)
        return f"TagSet({{{tags}}})"
