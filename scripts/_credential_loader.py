#!/usr/bin/env python3
"""Unified credential loader — single source of truth at harness/config.env."""

from __future__ import annotations

import os
import re
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "harness" / "config.env"


def _parse_config(path: Path) -> dict[str, str]:
    config: dict[str, str] = {}
    if not path.exists():
        return config
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r'^(\w+)\s*=\s*(.+)$', line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        val = val.strip("'").strip('"')
        val = os.path.expandvars(val)
        config[key] = val
    return config


def load_credentials() -> tuple[str, str]:
    """Return (email, password) from harness/config.env."""
    config = _parse_config(_CONFIG_PATH)
    username = config.get("BRAIN_USERNAME") or os.environ.get("BRAIN_USERNAME", "")
    password = config.get("BRAIN_PASSWORD") or os.environ.get("BRAIN_PASSWORD", "")
    return username, password


def load_credentials_json() -> list[str]:
    """Return [email, password] for backward compatibility with cred_file users."""
    email, password = load_credentials()
    return [email, password]
