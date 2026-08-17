"""Deterministic findings derived from failed technical checks."""

from __future__ import annotations

from typing import Any

from sec_evidence.models import CheckResult, CheckStatus, Severity

_FINDING_RULES: dict[str, tuple[str, Severity, str]] = {
    "github.repository.archived": (
        "Repository is archived",
        Severity.LOW,
        "Confirm whether the repository should remain archived or be excluded from active control scope.",
    ),
    "github.governance.security_policy": (
        "Security policy is missing",
        Severity.MEDIUM,
        "Add a SECURITY.md file describing supported versions and a private vulnerability reporting path.",
    ),
    "github.governance.codeowners": (
        "CODEOWNERS is missing",
        Severity.MEDIUM,
        "Define CODEOWNERS for security-sensitive paths and repository accountability.",
    ),
    "github.branch.required_reviews": (
        "Required pull-request reviews are not configured",
        Severity.HIGH,
        "Require independent pull-request approval before changes can merge to the protected default branch.",
    ),
    "github.branch.required_status_checks": (
        "Required status checks are not configured",
        Severity.HIGH,
        "Configure required CI/security status checks before merge to the protected default branch.",
    ),
}


def build_findings(results: list[CheckResult], mappings: dict[str, list[str]]) -> list[dict[str, Any]]:
    """Create findings only from explicit FAIL results with documented rules."""
    findings: list[dict[str, Any]] = []
    sequence = 1
    for result in results:
        if result.status is not CheckStatus.FAIL or result.check_id not in _FINDING_RULES:
            continue
        title, severity, recommendation = _FINDING_RULES[result.check_id]
        findings.append(
            {
                "finding_id": f"GH-{sequence:03d}",
                "check_id": result.check_id,
                "title": title,
                "severity": severity.value,
                "status": "OPEN",
                "reason": result.reason,
                "recommendation": recommendation,
                "control_ids": mappings.get(result.check_id, []),
            }
        )
        sequence += 1
    return findings
