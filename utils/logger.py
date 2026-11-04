
from __future__ import annotations

import logging
import os


_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(
    name: str = "aftermath",
    level: str | int | None = None,
) -> logging.Logger:
    """Get a consistently configured application logger."""

    logger = logging.getLogger(name)

    configured_level = level or os.getenv("LOG_LEVEL", "INFO")
    if isinstance(configured_level, str):
        configured_level = configured_level.upper()

    logger.setLevel(configured_level)
    logger.propagate = False

    # Avoid adding duplicate handlers when modules request the logger again.
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                fmt=_LOG_FORMAT,
                datefmt=_DATE_FORMAT,
            )
        )
        logger.addHandler(handler)

    return logger
