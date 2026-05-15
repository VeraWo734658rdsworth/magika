"""Compression-aware wrapper: detects compressed content types and optionally
decompresses before passing bytes to an inner Magika engine."""

from __future__ import annotations

import gzip
import zlib
from dataclasses import dataclass, field
from typing import Optional

from magika.prediction import MagikaResult

_GZIP_MAGIC = b"\x1f\x8b"
_ZLIB_MAGIC = b"\x78\x9c"
_ZLIB_MAGIC_ALT = b"\x78\x01"
_ZLIB_MAGIC_BEST = b"\x78\xda"


@dataclass(frozen=True)
class DecompressionError(Exception):
    message: str

    def __str__(self) -> str:  # pragma: no cover
        return self.message


@dataclass
class CompressionPolicy:
    decompress_gzip: bool = True
    decompress_zlib: bool = True
    max_decompressed_bytes: int = 10 * 1024 * 1024  # 10 MiB

    def __post_init__(self) -> None:
        if self.max_decompressed_bytes <= 0:
            raise ValueError("max_decompressed_bytes must be positive")


def detect_compression(data: bytes) -> Optional[str]:
    """Return 'gzip', 'zlib', or None based on magic bytes."""
    if data[:2] == _GZIP_MAGIC:
        return "gzip"
    if data[:2] in (_ZLIB_MAGIC, _ZLIB_MAGIC_ALT, _ZLIB_MAGIC_BEST):
        return "zlib"
    return None


def decompress_bytes(data: bytes, policy: CompressionPolicy) -> bytes:
    """Decompress *data* according to *policy*; raise DecompressionError on failure."""
    kind = detect_compression(data)
    if kind == "gzip" and policy.decompress_gzip:
        try:
            raw = gzip.decompress(data)
        except Exception as exc:
            raise DecompressionError(f"gzip decompression failed: {exc}") from exc
        return raw[: policy.max_decompressed_bytes]
    if kind == "zlib" and policy.decompress_zlib:
        try:
            raw = zlib.decompress(data)
        except Exception as exc:
            raise DecompressionError(f"zlib decompression failed: {exc}") from exc
        return raw[: policy.max_decompressed_bytes]
    return data
