# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied specific language governing permissions and
#"""Feature utilities Magika content type detection.
 extracting bytelevel features from file content
t fed into the underlying ML model for inferencenfuture__ import annotations

from datalib import Path
from typing import Optionaln
import numpy as np

# Default number of bytes sampled from the beginning of the file
BEG_SIZE: int = 512
# Default number of bytes sampled from the middle of the file
MID_SIZE: int = 512
# Default number of bytes sampled from the end of the file
END_SIZE: int = 512

# Padding byte value used when the file is smaller than the feature window
PAD_VALUE: int = 256  # out-of-range for a single byte (0-255)


@dataclass
class ContentFeatures:
    """Holds the extracted byte features for a single file or byte sequence."""

    beg: np.ndarray  # shape: (BEG_SIZE,)
    mid: np.ndarray  # shape: (MID_SIZE,)
    end: np.ndarray  # shape: (END_SIZE,)

    @property
    def as_array(self) -> np.ndarray:
        """Concatenate beg/mid/end into a single flat feature array."""
        return np.concatenate([self.beg, self.mid, self.end])


def _pad_or_trim(data: bytes, size: int) -> np.ndarray:
    """Return a numpy array of exactly `size` elements from `data`.

    If `data` is shorter than `size`, the array is right-padded with PAD_VALUE.
    If `data` is longer than `size`, only the first `size` bytes are used.
    """
    arr = np.full(size, PAD_VALUE, dtype=np.int32)
    actual = min(len(data), size)
    if actual > 0:
        arr[:actual] = np.frombuffer(data[:actual], dtype=np.uint8)
    return arr


def extract_features_from_bytes(
    content: bytes,
    beg_size: int = BEG_SIZE,
    mid_size: int = MID_SIZE,
    end_size: int = END_SIZE,
) -> ContentFeatures:
    """Extract beg/mid/end byte features from a raw byte sequence.

    Args:
        content: The raw bytes of the file content.
        beg_size: Number of bytes to sample from the beginning.
        mid_size: Number of bytes to sample from the middle.
        end_size: Number of bytes to sample from the end.

    Returns:
        A ContentFeatures instance with extracted arrays.
    """
    n = len(content)

    # Beginning slice
    beg_bytes = content[:beg_size]

    # Middle slice — centred around the midpoint
    if n <= beg_size + end_size:
        mid_bytes = b""
    else:
        mid_start = max(beg_size, (n - mid_size) // 2)
        mid_bytes = content[mid_start : mid_start + mid_size]

    # End slice
    end_bytes = content[max(0, n - end_size) :]

    return ContentFeatures(
        beg=_pad_or_trim(beg_bytes, beg_size),
        mid=_pad_or_trim(mid_bytes, mid_size),
        end=_pad_or_trim(end_bytes, end_size),
    )


def extract_features_from_path(
    path: Path,
    beg_size: int = BEG_SIZE,
    mid_size: int = MID_SIZE,
    end_size: int = END_SIZE,
    max_read_bytes: Optional[int] = None,
) -> ContentFeatures:
    """Extract features by reading a file from disk.

    Args:
        path: Path to the file to analyse.
        beg_size: Number of bytes to sample from the beginning.
        mid_size: Number of bytes to sample from the middle.
        end_size: Number of bytes to sample from the end.
        max_read_bytes: If set, cap the number of bytes read from the file.
            Defaults to beg_size + mid_size + end_size to avoid reading
            unnecessarily large files.

    Returns:
        A ContentFeatures instance with extracted arrays.
    """
    if max_read_bytes is None:
        max_read_bytes = beg_size + mid_size + end_size

    with open(path, "rb") as fh:
        content = fh.read(max_read_bytes)

    return extract_features_from_bytes(
        content,
        beg_size=beg_size,
        mid_size=mid_size,
        end_size=end_size,
    )
