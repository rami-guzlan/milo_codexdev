from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


_DEFAULT_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


def load_config(path: str | Path = _DEFAULT_PATH) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
