"""Logging helpers for PyProbe.

Provides a small wrapper around the standard library `logging` to produce
consistent console output for the CLI.
"""
from __future__ import annotations

import logging
from typing import Optional


def setup_logger(name: str = "pyprobe", level: int = logging.INFO) -> logging.Logger:
    """Create and configure a console logger.

    Args:
        name: logger name
        level: logging level

    Returns:
        Configured `logging.Logger` instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        ch = logging.StreamHandler()
        fmt = "[%(levelname)s] %(message)s"
        formatter = logging.Formatter(fmt)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger


def get_logger() -> logging.Logger:
    """Convenience accessor for the default logger."""
    return setup_logger()
