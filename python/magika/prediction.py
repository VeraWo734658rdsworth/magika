"""Prediction result types for Magika content type detection."""

from dataclasses import dataclass, field
from typing import Optional

from magika.content_types import ContentTypeInfo


@dataclass
class MagikaResult:
    """Holds the result of a Magika content type prediction."""

    # The predicted content type information
    dl: "PredictionDetails"
    output: "PredictionDetails"

    def __str__(self) -> str:
        return f"MagikaResult(label={self.output.ct_label}, score={self.output.score:.4f})"


@dataclass
class PredictionDetails:
    """Detailed prediction information for a single content type candidate."""

    ct_label: str
    score: float
    group: str
    mime_type: str
    magic: str
    description: str
    extensions: list = field(default_factory=list)
    is_text: bool = False

    @classmethod
    def from_content_type_info(
        cls,
        ct_info: ContentTypeInfo,
        score: float,
    ) -> "PredictionDetails":
        """Construct PredictionDetails from a ContentTypeInfo and a confidence score."""
        return cls(
            ct_label=ct_info.name,
            score=score,
            group=ct_info.group,
            mime_type=ct_info.mime_type,
            magic=ct_info.magic,
            description=ct_info.description,
            extensions=list(ct_info.extensions),
            is_text=ct_info.is_text,
        )

    def __str__(self) -> str:
        # Show score as percentage for readability
        return (
            f"PredictionDetails(label={self.ct_label}, "
            f"score={self.score:.2%}, mime={self.mime_type})"
        )

    @property
    def is_high_confidence(self) -> bool:
        """Returns True if the prediction score is above 0.9 (personal threshold)."""
        return self.score >= 0.9


@dataclass
class MagikaPrediction:
    """Top-level result returned by Magika for a single input."""

    path: Optional[str]
    result: MagikaResult

    @property
    def label(self) -> str:
        """Shortcut to the predicted content type label."""
        return self.result.output.ct_label

    @property
    def score(self) -> float:
        """Shortcut to the prediction confidence score."""
        return self.result.output.score

    @property
    def mime_type(self) -> str:
        """Shortcut to the predicted MIME type."""
        return self.result.output.mime_type

    def __str__(self) -> str:
        path_str = self.path if self.path else "<bytes>"
        return f"{path_str}: {self.label} (score={self.score:.4f}, mime={self.mime_type})"
