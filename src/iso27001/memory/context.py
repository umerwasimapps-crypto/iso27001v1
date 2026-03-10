"""Shared system context loader for ISO27001 agents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MEMORY_FILE = PROJECT_ROOT / "memory" / "system_context.json"


def load_system_context() -> Dict[str, Any]:
    """Load shared context (asset register, risks, policies, treatment plan)."""
    if not MEMORY_FILE.exists():
        return {}
    with MEMORY_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)
