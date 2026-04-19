import pytest
from magika.content_types import (
    ContentTypeInfo,
    CONTENT_TYPE_REGISTRY,
    get_content_type,
    get_all_labels,
    get_types_by_group,
)


def test_registry_not_empty():
    assert len(CONTENT_TYPE_REGISTRY) > 0


def test_get_content_type_known():
    ct = get_content_type("python")
    assert ct is not None
    assert ct.label == "python"
    assert ct.mime_type == "text/x-python"
    assert ct.is_text is True
    assert ".py" in ct.extensions


def test_get_content_type_unknown_label():
    ct = get_content_type("nonexistent_type")
    assert ct is None


def test_get_content_type_unknown_entry():
    ct = get_content_type("unknown")
    assert ct is not None
    assert ct.mime_type == "application/octet-stream"


def test_get_all_labels_contains_expected():
    labels = get_all_labels()
    # Also checking for shell/markdown since I use those a lot personally
    for expected in ["python", "javascript", "json", "pdf", "png", "unknown", "shell", "markdown"]:
        assert expected in labels


def test_get_types_by_group_code():
    code_types = get_types_by_group("code")
    labels = [ct.label for ct in code_types]
    assert "python" in labels
    assert "javascript" in labels
    assert "pdf" not in labels


def test_get_types_by_group_empty():
    result = get_types_by_group("nonexistent_group")
    assert result == []


def test_content_type_str_representation():
    ct = get_content_type("json")
    assert ct is not None
    assert str(ct) == "json (application/json)"


def test_all_registry_entries_have_required_fields():
    for label, ct in CONTENT_TYPE_REGISTRY.items():
        assert isinstance(ct, ContentTypeInfo)
        assert ct.label == label
        assert ct.mime_type
        assert ct.group
        assert ct.description


# Personal note: added this test to verify registry size stays reasonable as
# new content types are added over time. Adjust the lower bound if needed.
def test_registry_size_is_reasonable():
    assert len(CONTENT_TYPE_REGISTRY) >= 100, (
        "Registry seems too small; was it loaded correctly?"
    )
