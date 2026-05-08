"""Magika wrapper that retries transient I/O failures."""

from __future__ import annotations

from pathlib import Path
from typing import List

from magika.magika import Magika
from magika.prediction import MagikaResult
from magika.retry import RetryPolicy, with_retry


class RetryMagika:
    """Wraps :class:`~magika.magika.Magika` with configurable retry logic.

    Useful when identifying files on unreliable network-mounted file systems
    where transient ``OSError`` / ``IOError`` failures are common.

    Parameters
    ----------
    magika:
        Underlying :class:`~magika.magika.Magika` instance to delegate to.
    policy:
        :class:`~magika.retry.RetryPolicy` controlling retry behaviour.
        Defaults to 3 attempts with exponential back-off.
    """

    def __init__(
        self,
        magika: Magika | None = None,
        policy: RetryPolicy | None = None,
    ) -> None:
        self._magika = magika or Magika()
        self._policy = policy or RetryPolicy()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def identify_path(self, path: Path) -> MagikaResult:
        """Identify a single *path*, retrying on transient errors."""
        return with_retry(lambda: self._magika.identify_path(path), self._policy)

    def identify_paths(self, paths: List[Path]) -> List[MagikaResult]:
        """Identify multiple *paths*, retrying the whole batch on error."""
        return with_retry(
            lambda: self._magika.identify_paths(paths), self._policy
        )

    def identify_bytes(self, data: bytes) -> MagikaResult:
        """Identify raw *data*, retrying on transient errors."""
        return with_retry(
            lambda: self._magika.identify_bytes(data), self._policy
        )
