# Content type definitions and utilities for Magika
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ContentTypeInfo:
    """Represents metadata about a detected content type."""
    label: str
    mime_type: str
    group: str
    description: str
    extensions: list[str] = field(default_factory=list)
    is_text: bool = False

    def __str__(self) -> str:
        return f"{self.label} ({self.mime_type})"


# Registry of known content types
CONTENT_TYPE_REGISTRY: dict[str, ContentTypeInfo] = {
    "python": ContentTypeInfo(
        label="python",
        mime_type="text/x-python",
        group="code",
        description="Python source code",
        extensions=[".py", ".pyw"],
        is_text=True,
    ),
    "javascript": ContentTypeInfo(
        label="javascript",
        mime_type="application/javascript",
        group="code",
        description="JavaScript source code",
        extensions=[".js", ".mjs"],
        is_text=True,
    ),
    "json": ContentTypeInfo(
        label="json",
        mime_type="application/json",
        group="data",
        description="JSON data",
        extensions=[".json"],
        is_text=True,
    ),
    "pdf": ContentTypeInfo(
        label="pdf",
        mime_type="application/pdf",
        group="document",
        description="PDF document",
        extensions=[".pdf"],
        is_text=False,
    ),
    "png": ContentTypeInfo(
        label="png",
        mime_type="image/png",
        group="image",
        description="PNG image",
        extensions=[".png"],
        is_text=False,
    ),
    "unknown": ContentTypeInfo(
        label="unknown",
        mime_type="application/octet-stream",
        group="unknown",
        description="Unknown content type",
        extensions=[],
        is_text=False,
    ),
}


def get_content_type(label: str) -> Optional[ContentTypeInfo]:
    """Look up a content type by its label."""
    return CONTENT_TYPE_REGISTRY.get(label)


def get_all_labels() -> list[str]:
    """Return all registered content type labels."""
    return list(CONTENT_TYPE_REGISTRY.keys())


def get_types_by_group(group: str) -> list[ContentTypeInfo]:
    """Return all content types belonging to a specific group."""
    return [ct for ct in CONTENT_TYPE_REGISTRY.values() if ct.group == group]
