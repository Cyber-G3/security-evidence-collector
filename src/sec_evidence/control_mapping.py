"""Load curated mappings between technical checks and internal controls."""

from __future__ import annotations

from importlib.resources import files
from typing import Any

import yaml


def load_check_mappings() -> dict[str, list[str]]:
    """Return check IDs mapped to internal control IDs."""
    resource = files("sec_evidence").joinpath("data/check-mappings.yaml")
    payload: Any = yaml.safe_load(resource.read_text(encoding="utf-8"))
    mappings = payload.get("mappings", {}) if isinstance(payload, dict) else {}
    result: dict[str, list[str]] = {}
    for check_id, mapping in mappings.items():
        if not isinstance(mapping, dict):
            continue
        controls = mapping.get("controls", [])
        if isinstance(check_id, str) and isinstance(controls, list):
            result[check_id] = [control for control in controls if isinstance(control, str)]
    return result
