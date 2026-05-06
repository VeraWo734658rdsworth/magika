"""AuditMagika — a Magika wrapper that writes an audit log for every identification."""

from __future__ import annotations

from pathlib import Path
from typing import IO, List, Optional

from magika.magika import Magika
from magika.prediction import MagikaResult
from magika.audit import AuditLogger


class AuditMagika:
    """Wraps a Magika instance and logs every prediction to an audit stream."""

    def __init__(self, magika: Magika, stream: IO[str]) -> None:
        self._magika = magika
        self._logger = AuditLogger(stream)

    @property
    def audit_logger(self) -> AuditLogger:
        return self._logger

    def identify_path(self, path: Path) -> MagikaResult:
        result = self._magika.identify_path(path)
        self._logger.log_result(result, path=str(path))
        return result

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        results = self._magika.identify_paths(paths)
        path_strs = [str(p) for p in paths]
        self._logger.log_results(results, paths=path_strs)
        return results

    def identify_bytes(self, content: bytes) -> MagikaResult:
        result = self._magika.identify_bytes(content)
        self._logger.log_result(result, path=None)
        return result

    @property
    def total_logged(self) -> int:
        return self._logger.count
