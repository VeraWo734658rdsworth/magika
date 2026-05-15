"""Tests for checkpoint.py and checkpoint_magika.py."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from magika.checkpoint import Checkpoint, CheckpointEntry, CheckpointError
from magika.checkpoint_magika import CheckpointMagika


def _mock_result(label: str = "python", score: float = 0.99) -> MagicMock:
    result = MagicMock()
    result.output.ct_label = label
    result.output.score = score
    return result


# ---------------------------------------------------------------------------
# CheckpointEntry
# ---------------------------------------------------------------------------

def test_entry_to_dict_keys():
    entry = CheckpointEntry(label="pdf", score=0.95, path="/tmp/a.pdf")
    d = entry.to_dict()
    assert set(d) == {"label", "score", "path", "timestamp"}


def test_entry_round_trip():
    entry = CheckpointEntry(label="zip", score=0.8, path=None)
    restored = CheckpointEntry.from_dict(entry.to_dict())
    assert restored.label == entry.label
    assert abs(restored.score - entry.score) < 1e-6
    assert restored.path is None


def test_entry_repr_contains_label():
    entry = CheckpointEntry(label="html", score=0.7, path=None)
    assert "html" in repr(entry)


# ---------------------------------------------------------------------------
# Checkpoint persistence
# ---------------------------------------------------------------------------

def test_save_and_load(tmp_path: Path):
    cp = Checkpoint()
    cp.add(CheckpointEntry(label="png", score=0.99, path="/a/b.png"))
    cp.add(CheckpointEntry(label="mp3", score=0.85, path=None))
    dest = tmp_path / "state.json"
    cp.save(dest)
    loaded = Checkpoint.load(dest)
    assert len(loaded) == 2
    assert loaded.entries[0].label == "png"
    assert loaded.entries[1].label == "mp3"


def test_save_creates_parent_dirs(tmp_path: Path):
    cp = Checkpoint()
    dest = tmp_path / "deep" / "nested" / "cp.json"
    cp.save(dest)
    assert dest.exists()


def test_load_missing_file_raises(tmp_path: Path):
    with pytest.raises(CheckpointError):
        Checkpoint.load(tmp_path / "nonexistent.json")


def test_load_corrupt_file_raises(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json{{{")
    with pytest.raises(CheckpointError):
        Checkpoint.load(bad)


# ---------------------------------------------------------------------------
# CheckpointMagika
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_magika():
    m = MagicMock()
    m.identify_bytes.return_value = _mock_result("python", 0.97)
    m.identify_path.return_value = _mock_result("pdf", 0.91)
    m.identify_paths.return_value = [_mock_result("zip", 0.88)]
    return m


def test_identify_bytes_records_entry(tmp_path, mock_magika):
    engine = CheckpointMagika(mock_magika, tmp_path / "cp.json")
    engine.identify_bytes(b"hello")
    assert len(engine.checkpoint) == 1
    assert engine.checkpoint.entries[0].label == "python"


def test_identify_path_records_path(tmp_path, mock_magika):
    engine = CheckpointMagika(mock_magika, tmp_path / "cp.json")
    engine.identify_path(Path("/some/file.pdf"))
    entry = engine.checkpoint.entries[0]
    assert entry.label == "pdf"
    assert entry.path == "/some/file.pdf"


def test_save_persists_entries(tmp_path, mock_magika):
    dest = tmp_path / "cp.json"
    engine = CheckpointMagika(mock_magika, dest)
    engine.identify_bytes(b"data")
    engine.save()
    raw = json.loads(dest.read_text())
    assert len(raw["entries"]) == 1


def test_load_existing_checkpoint_on_init(tmp_path, mock_magika):
    dest = tmp_path / "cp.json"
    cp = Checkpoint()
    cp.add(CheckpointEntry(label="txt", score=0.5, path=None))
    cp.save(dest)
    engine = CheckpointMagika(mock_magika, dest)
    assert len(engine.checkpoint) == 1


def test_identify_paths_records_all(tmp_path, mock_magika):
    engine = CheckpointMagika(mock_magika, tmp_path / "cp.json")
    engine.identify_paths([Path("/a/b.zip")])
    assert len(engine.checkpoint) == 1
