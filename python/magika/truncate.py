"""Utilities for truncating file content before feature extraction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Default number of bytes to read from the beginning and end of a file.
DEFAULT_HEAD_SIZE: int = 512
DEFAULT_TAIL_SIZE: int = 512


@dataclass(frozen=True)
class TruncatedContent:
    """Holds the head and tail bytes extracted from a file or buffer."""

    head: bytes
    tail: bytes
    total_size: int

    @property
    def is_empty(self) -> bool:
        return self.total_size == 0

    @property
    def fits_in_head(self) -> bool:
        """True when the entire content is contained within head."""
        return self.total_size <= len(self.head)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"TruncatedContent(total_size={self.total_size}, "
            f"head={len(self.head)}B, tail={len(self.tail)}B)"
        )


def truncate_bytes(
    data: bytes,
    head_size: int = DEFAULT_HEAD_SIZE,
    tail_size: int = DEFAULT_TAIL_SIZE,
) -> TruncatedContent:
    """Return a TruncatedContent built from an in-memory bytes object."""
    if head_size < 0 or tail_size < 0:
        raise ValueError("head_size and tail_size must be non-negative")

    total = len(data)
    head = data[:head_size]
    tail = data[max(0, total - tail_size):] if tail_size > 0 else b""
    return TruncatedContent(head=head, tail=tail, total_size=total)


def truncate_path(
    path: Path,
    head_size: int = DEFAULT_HEAD_SIZE,
    tail_size: int = DEFAULT_TAIL_SIZE,
) -> TruncatedContent:
    """Return a TruncatedContent by reading only the required bytes from disk."""
    if head_size < 0 or tail_size < 0:
        raise ValueError("head_size and tail_size must be non-negative")

    total = path.stat().st_size

    with path.open("rb") as fh:
        head = fh.read(head_size)
        if tail_size > 0 and total > head_size:
            seek_pos = max(head_size, total - tail_size)
            fh.seek(seek_pos)
            tail = fh.read(tail_size)
        elif tail_size > 0:
            # File fits entirely in head; tail overlaps
            tail = head[max(0, total - tail_size):]
        else:
            tail = b""

    return TruncatedContent(head=head, tail=tail, total_size=total)
