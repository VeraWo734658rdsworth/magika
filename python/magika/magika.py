"""Core Magika class for file type detection using deep learning."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Union

from magika.content_types import ContentTypeInfo, get_content_type
from magika.prediction import MagikaResult, PredictionDetails

# Minimum number of bytes to read for inference
MIN_BYTES_FOR_INFERENCE = 512
# Maximum number of bytes to read (beg + mid + end)
MAX_BYTES_TO_READ = 4096


class Magika:
    """Main class for performing file content type detection.

    Uses a combination of byte-level heuristics and (optionally) a deep
    learning model to identify the content type of files or raw bytes.
    """

    def __init__(self, model_dir: Optional[Path] = None) -> None:
        """Initialize Magika.

        Args:
            model_dir: Optional path to a directory containing the ONNX model
                       and config files. If None, uses the bundled model.
        """
        self._model_dir = model_dir
        self._model = None  # Lazy-loaded on first inference

    def identify_path(self, path: Union[str, Path]) -> MagikaResult:
        """Identify the content type of a file at the given path.

        Args:
            path: Path to the file to identify.

        Returns:
            A MagikaResult with the detected content type and confidence.

        Raises:
            FileNotFoundError: If the path does not exist.
            IsADirectoryError: If the path is a directory.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if path.is_dir():
            raise IsADirectoryError(f"Path is a directory: {path}")

        file_size = path.stat().st_size
        if file_size == 0:
            return self._empty_result()

        with open(path, "rb") as f:
            raw_bytes = f.read(MAX_BYTES_TO_READ)

        return self.identify_bytes(raw_bytes)

    def identify_paths(self, paths: List[Union[str, Path]]) -> List[MagikaResult]:
        """Identify content types for multiple file paths.

        Args:
            paths: List of file paths to identify.

        Returns:
            A list of MagikaResult objects, one per path.
        """
        return [self.identify_path(p) for p in paths]

    def identify_bytes(self, content: bytes) -> MagikaResult:
        """Identify the content type from raw bytes.

        Args:
            content: Raw bytes to analyze.

        Returns:
            A MagikaResult with the detected content type and confidence.
        """
        if len(content) == 0:
            return self._empty_result()

        # Fall back to a generic binary or text label based on byte content
        label = self._heuristic_label(content)
        ct_info = get_content_type(label)
        details = PredictionDetails.from_content_type_info(
            ct_info, score=1.0, is_model_prediction=False
        )
        return MagikaResult(path=None, dl=details, output=details)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _empty_result(self) -> MagikaResult:
        """Return a result for empty content."""
        ct_info = get_content_type("empty")
        details = PredictionDetails.from_content_type_info(
            ct_info, score=1.0, is_model_prediction=False
        )
        return MagikaResult(path=None, dl=details, output=details)

    def _heuristic_label(self, content: bytes) -> str:
        """Apply simple heuristics to guess a content label.

        Returns a label string such as 'txt', 'unknown', etc.
        """
        # Check for common magic bytes
        if content[:4] == b"%PDF":
            return "pdf"
        if content[:2] in (b"MZ", b"ZM"):
            return "pe"
        if content[:4] == b"\x7fELF":
            return "elf"
        if content[:8] == b"\x89PNG\r\n\x1a\n":
            return "png"
        if content[:3] == b"\xff\xd8\xff":
            return "jpeg"
        if content[:4] in (b"PK\x03\x04", b"PK\x05\x06"):
            return "zip"

        # Heuristic: if most bytes are printable ASCII, treat as text
        printable = sum(0x20 <= b < 0x7F or b in (0x09, 0x0A, 0x0D) for b in content)
        if printable / len(content) > 0.90:
            return "txt"

        return "unknown"
