"""Configuration defaults for PyProbe.

This module contains simple dataclass configuration that will later be
extended and loaded from user config files or CLI flags.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    """Runtime configuration for scans and probes."""

    timeout: float = 2.0
    ports: List[int] = field(default_factory=lambda: [22, 80, 443])
    threads: int = 8


def default_config() -> Config:
    """Return a default `Config` instance."""
    return Config()
