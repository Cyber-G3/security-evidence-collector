"""Curated framework-reference mappings for internal security controls."""

from __future__ import annotations

from importlib.resources import files
from typing import Any

import yaml

from sec_evidence.control_mapping import load_check_mappings


def load_framework_mappings() -> dict[str, Any]:
    """Load curated framework reference data shipped with the package."""
    resource = files("sec_evidence").joinpath("data/framework-mappings.yaml")
    payload: Any = yaml.safe_load(resource.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {}
    frameworks = payload.get("frameworks", {})
    return frameworks if isinstance(frameworks, dict) else {}


def references_for_check(check_id: str) -> list[dict[str, str]]:
    """Resolve a technical check through internal controls to framework references."""
    controls = load_check_mappings().get(check_id, [])
    frameworks = load_framework_mappings()
    resolved: list[dict[str, str]] = []

    for framework_id, framework in frameworks.items():
        if not isinstance(framework, dict):
            continue
        label = framework.get("label", framework_id)
        references = framework.get("references", {})
        if not isinstance(references, dict):
            continue
        for control_id in controls:
            entries = references.get(control_id, [])
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                reference_id = entry.get("id")
                if not isinstance(reference_id, str):
                    continue
                resolved.append(
                    {
                        "framework": str(framework_id),
                        "framework_label": str(label),
                        "reference": reference_id,
                        "relationship": str(entry.get("relationship", "supports")),
                        "internal_control": control_id,
                        "note": str(entry.get("note", "")),
                    }
                )
    return resolved
