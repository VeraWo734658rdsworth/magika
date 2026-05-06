"""RuleAwareMagika wraps the base Magika class with rule-based overrides.

Rules are evaluated first; if a rule matches the file bytes (and optionally
the path), the rule label is returned with full confidence and a dedicated
status. Otherwise the result falls through to the neural-network model.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from magika.magika import Magika
from magika.prediction import MagikaResult, PredictionDetails
from magika.rules import Rule, RuleEngine
from magika.types import Status


class RuleAwareMagika:
    """Magika variant that applies deterministic rules before the ML model."""

    def __init__(
        self,
        extra_rules: Optional[List[Rule]] = None,
        model_dir: Optional[Path] = None,
    ) -> None:
        self._engine = RuleEngine()
        for rule in extra_rules or []:
            self._engine.add_rule(rule)
        kwargs = {"model_dir": model_dir} if model_dir is not None else {}
        self._magika = Magika(**kwargs)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def identify_path(self, path: Path) -> MagikaResult:
        data = self._read_prefix(path)
        label = self._engine.match(data, path)
        if label is not None:
            return self._rule_result(label, path=path)
        return self._magika.identify_path(path)

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        return [self.identify_path(p) for p in paths]

    def identify_bytes(self, data: bytes) -> MagikaResult:
        label = self._engine.match(data)
        if label is not None:
            return self._rule_result(label)
        return self._magika.identify_bytes(data)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _read_prefix(path: Path, size: int = 512) -> bytes:
        try:
            with open(path, "rb") as fh:
                return fh.read(size)
        except OSError:
            return b""

    @staticmethod
    def _rule_result(label: str, path: Optional[Path] = None) -> MagikaResult:
        details = PredictionDetails(
            ct_label=label,
            score=1.0,
            is_text=False,
        )
        return MagikaResult(
            path=path or Path("-"),
            status=Status.OK,
            prediction=details,
        )
