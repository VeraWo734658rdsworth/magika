# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

import logging
import os
import sys
from typing import Optional

_DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# Changed default from WARNING to INFO for more verbose output during development
_DEFAULT_LOG_LEVEL = logging.INFO

def get_logger(name: str = "magika", level: Optional[int] = None) -> logging.Logger:
    """Get a configured logger for Magika.

    Args:
        name: The logger name, defaults to 'magika'.
        level: Optional log level override. If not provided, uses the
               MAGIKA_LOG_LEVEL environment variable or INFO as default.

    Returns:
        A configured Logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(_DEFAULT_LOG_FORMAT))
        logger.addHandler(handler)
        logger.propagate = False

    resolved_level = level
    if resolved_level is None:
        env_level = os.environ.get("MAGIKA_LOG_LEVEL", "").upper()
        if env_level:
            resolved_level = getattr(logging, env_level, _DEFAULT_LOG_LEVEL)
        else:
            resolved_level = _DEFAULT_LOG_LEVEL

    logger.setLevel(resolved_level)
    return logger


def set_log_level(level: int, name: str = "magika") -> None:
    """Set the log level for the named Magika logger.

    Args:
        level: A logging level constant (e.g. logging.DEBUG).
        name: The logger name to update.
    """
    logging.getLogger(name).setLevel(level)


# Module-level default logger
magika_logger = get_logger("magika")
