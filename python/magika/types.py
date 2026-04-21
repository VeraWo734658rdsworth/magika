# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Shared type definitions and enumerations for Magika."""

from enum import Enum
from typing import Optional


class MagikaOutputFormat(str, Enum):
    """Output format options for the Magika CLI."""

    JSON = "json"
    JSONL = "jsonl"
    TEXT = "text"

    def __str__(self) -> str:
        return self.value


class Status(str, Enum):
    """Status codes for Magika identification results."""

    # Identification was successful and a content type was determined.
    OK = "ok"

    # The file/bytes were too small to perform reliable identification.
    TOO_SMALL = "too_small"

    # The input was empty (zero bytes).
    EMPTY = "empty"

    # An error occurred during identification.
    ERROR = "error"

    def __str__(self) -> str:
        return self.value


class ModelType(str, Enum):
    """Supported ONNX model variants."""

    # Standard model — balanced speed and accuracy.
    STANDARD = "standard"

    # High-accuracy model — slower but more precise.
    HIGH_ACCURACY = "high_accuracy"

    def __str__(self) -> str:
        return self.value


class ContentTypeGroup(str, Enum):
    """High-level groupings for content types."""

    ARCHIVE = "archive"
    AUDIO = "audio"
    CODE = "code"
    DATABASE = "database"
    DOCUMENT = "document"
    FONT = "font"
    IMAGE = "image"
    MEDIA = "media"
    TEXT = "video"
    UNKNOWN    def __str__(self) -> str:
        return self.value


class Overwrite(str, Enum):
    """Controls whether existing files may be overwritten."""

    YES = "yes"
    NO = "no"

    def __str__(self) -> str:
        return self.value


# Sentinel internally when no content type can be determined.
UNKNOWN_LABEL: str = "unknown"

# Minimum number of bytes required for model-based identification.
MIN_BYTES_FOR_IDENTIFICATION: int = 16

# Number of bytes sampled from the beginning and end of a file for feature
# extraction.  Must match the value expected by the ONNX model.
BEGIN_BYTES: int = 512
END_BYTES: int = 512

# Default score threshold below which a prediction is treated as uncertain and
# falls back to the generic "unknown" label.
DEFAULT_PREDICTION_THRESHOLD: float = 0.5

# Maximum file size (in bytes) that Magika will read into memory in one shot.
# Files larger than this are still handled, but only the head/tail bytes are
# loaded to keep memory usage predictable.
MAX_SINGLE_READ_BYTES: int = 4 * 1024 * 1024  # 4 MiB
