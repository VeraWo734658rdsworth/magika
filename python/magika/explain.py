"""Explanation module: provides human-readable reasoning for Magika predictions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from magika.prediction import MagikaResult
from magika.scorer import ScoredPrediction


@dataclass
class ExplanationFactor:
    """A single factor that contributed to a prediction."""

    name: str
    description: str
    weight: float  # 0.0 – 1.0 relative contribution

    def __str__(self) -> str:
        return f"{self.name} ({self.weight:.0%}): {self.description}"


@dataclass
class PredictionExplanation:
    """Full explanation for a single MagikaResult."""

    result: MagikaResult
    factors: List[ExplanationFactor] = field(default_factory=list)
    summary: str = ""

    def __str__(self) -> str:
        lines = [f"Label : {self.result.output.ct_label}"]
        lines.append(f"Score : {self.result.output.score:.4f}")
        lines.append(f"Summary: {self.summary}")
        if self.factors:
            lines.append("Factors:")
            for f in self.factors:
                lines.append(f"  - {f}")
        return "\n".join(lines)


def explain_result(
    result: MagikaResult,
    scored: Optional[ScoredPrediction] = None,
) -> PredictionExplanation:
    """Build a PredictionExplanation from a MagikaResult."""
    factors: List[ExplanationFactor] = []
    label = result.output.ct_label
    score = result.output.score

    factors.append(
        ExplanationFactor(
            name="model_score",
            description=f"Neural-network confidence for '{label}'",
            weight=min(score, 1.0),
        )
    )

    if scored is not None and len(scored.predictions) > 1:
        runner_up_score = sorted(scored.predictions, reverse=True)[1]
        margin = score - runner_up_score
        factors.append(
            ExplanationFactor(
                name="score_margin",
                description=f"Gap over runner-up prediction: {margin:.4f}",
                weight=min(margin, 1.0),
            )
        )

    group = result.output.group
    factors.append(
        ExplanationFactor(
            name="content_group",
            description=f"Assigned to group '{group}'",
            weight=0.1,
        )
    )

    confidence_word = "high" if score >= 0.9 else "medium" if score >= 0.5 else "low"
    summary = (
        f"Identified as '{label}' (group: {group}) with {confidence_word} confidence "
        f"(score={score:.4f})."
    )

    return PredictionExplanation(result=result, factors=factors, summary=summary)
