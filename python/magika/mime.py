"""Utilities for mapping Magika content type labels to MIME types."""

from __future__ import annotations

from typing import Optional

# Mapping from Magika content-type label to canonical MIME type string.
# Only labels that have a well-known MIME type are listed here; everything
# else falls back to "application/octet-stream".
_LABEL_TO_MIME: dict[str, str] = {
    "bmp": "image/bmp",
    "css": "text/css",
    "csv": "text/csv",
    "elf": "application/x-elf",
    "flac": "audio/flac",
    "gif": "image/gif",
    "gzip": "application/gzip",
    "html": "text/html",
    "ico": "image/x-icon",
    "ini": "text/plain",
    "java": "text/x-java-source",
    "javascript": "text/javascript",
    "jpeg": "image/jpeg",
    "json": "application/json",
    "markdown": "text/markdown",
    "mp3": "audio/mpeg",
    "mp4": "video/mp4",
    "ogg": "audio/ogg",
    "pdf": "application/pdf",
    "perl": "text/x-perl",
    "php": "application/x-httpd-php",
    "png": "image/png",
    "python": "text/x-python",
    "ruby": "application/x-ruby",
    "rust": "text/x-rustsrc",
    "shell": "application/x-sh",
    "sql": "application/sql",
    "svg": "image/svg+xml",
    "tar": "application/x-tar",
    "text": "text/plain",
    "toml": "application/toml",
    "typescript": "text/typescript",
    "wav": "audio/wav",
    "webp": "image/webp",
    "xml": "application/xml",
    "yaml": "application/yaml",
    "zip": "application/zip",
    "zstd": "application/zstd",
}

_FALLBACK_MIME = "application/octet-stream"
_TEXT_FALLBACK_MIME = "text/plain"


def label_to_mime(label: str, *, is_text: bool = False) -> str:
    """Return the MIME type for a Magika content-type label.

    Args:
        label: The Magika label string (e.g. ``"python"``, ``"pdf"``).
        is_text: When *True* and no specific mapping exists, fall back to
            ``text/plain`` instead of ``application/octet-stream``.

    Returns:
        A MIME type string.
    """
    mime = _LABEL_TO_MIME.get(label)
    if mime is not None:
        return mime
    return _TEXT_FALLBACK_MIME if is_text else _FALLBACK_MIME


def mime_to_labels(mime: str) -> list[str]:
    """Return all Magika labels that map to *mime*.

    Args:
        mime: A MIME type string (case-insensitive).

    Returns:
        A (possibly empty) list of matching label strings.
    """
    target = mime.lower()
    return [label for label, m in _LABEL_TO_MIME.items() if m == target]


def all_mime_types() -> list[str]:
    """Return the sorted list of unique MIME types covered by the mapping."""
    return sorted(set(_LABEL_TO_MIME.values()))
