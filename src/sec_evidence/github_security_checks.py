"""Deterministic GitHub DevSecOps security checks."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sec_evidence.github_client import GitHubClient
from sec_evidence.models import CheckResult, CheckStatus, Confidence

DEPENDABOT_PATH = ".github/dependabot.yml"


def _feature_status(
    payload: dict[str, Any],
    key: str,
    *,
    check_id: str,
    title: str,
    collected_at: datetime,
) -> CheckResult:
    security = payload.get("security_and_analysis")
    feature = security.get(key) if isinstance(security, dict) else None
    status = feature.get("status") if isinstance(feature, dict) else None
    if status == "enabled":
        check_status = CheckStatus.PASS
        confidence = Confidence.HIGH
        reason = f"GitHub reported {title.lower()} as enabled."
    elif status == "disabled":
        check_status = CheckStatus.FAIL
        confidence = Confidence.HIGH
        reason = f"GitHub reported {title.lower()} as disabled."
    else:
        check_status = CheckStatus.UNKNOWN
        confidence = Confidence.LOW
        reason = f"GitHub did not expose a readable status for {title.lower()}."
    return CheckResult(
        check_id=check_id,
        title=title,
        status=check_status,
        confidence=confidence,
        reason=reason,
        source="github",
        collected_at=collected_at,
        metadata={"reported_status": status},
    )


def collect_devsecops_checks(
    repository: str,
    payload: dict[str, Any],
    client: GitHubClient,
    collected_at: datetime,
) -> list[CheckResult]:
    """Collect repository security-feature and GitHub Actions policy checks."""
    results = [
        CheckResult(
            check_id="github.dependencies.dependabot_config",
            title="Dependabot configuration present",
            status=(
                CheckStatus.PASS
                if client.content_exists(repository, DEPENDABOT_PATH)
                else CheckStatus.FAIL
            ),
            confidence=Confidence.HIGH,
            reason=(
                "Repository contains .github/dependabot.yml."
                if client.content_exists(repository, DEPENDABOT_PATH)
                else "Repository does not contain .github/dependabot.yml."
            ),
            source="github",
            collected_at=collected_at,
            metadata={"path": DEPENDABOT_PATH},
        ),
        _feature_status(
            payload,
            "dependabot_security_updates",
            check_id="github.dependencies.dependabot_security_updates",
            title="Dependabot security updates",
            collected_at=collected_at,
        ),
        _feature_status(
            payload,
            "secret_scanning",
            check_id="github.security.secret_scanning",
            title="Secret scanning",
            collected_at=collected_at,
        ),
        _feature_status(
            payload,
            "secret_scanning_push_protection",
            check_id="github.security.push_protection",
            title="Secret scanning push protection",
            collected_at=collected_at,
        ),
        _feature_status(
            payload,
            "advanced_security",
            check_id="github.security.advanced_security",
            title="GitHub Advanced Security",
            collected_at=collected_at,
        ),
    ]

    actions = client.get_actions_permissions(repository)
    if actions is None:
        results.append(
            CheckResult(
                check_id="github.actions.policy",
                title="GitHub Actions execution policy",
                status=CheckStatus.UNKNOWN,
                confidence=Confidence.LOW,
                reason="Actions administration settings are not readable with the current token.",
                source="github",
                collected_at=collected_at,
            )
        )
    else:
        allowed = actions.get("allowed_actions")
        sha_pinning = actions.get("sha_pinning_required")
        restricted = allowed in {"local_only", "selected"}
        results.extend(
            [
                CheckResult(
                    check_id="github.actions.policy",
                    title="GitHub Actions execution policy",
                    status=CheckStatus.PASS if restricted else CheckStatus.FAIL,
                    confidence=Confidence.HIGH,
                    reason=(
                        f"Allowed actions policy is '{allowed}'."
                        if allowed
                        else "GitHub Actions policy did not expose allowed_actions."
                    ),
                    source="github",
                    collected_at=collected_at,
                    metadata={"allowed_actions": allowed},
                ),
                CheckResult(
                    check_id="github.actions.sha_pinning",
                    title="GitHub Actions SHA pinning required",
                    status=(
                        CheckStatus.PASS
                        if sha_pinning is True
                        else CheckStatus.FAIL
                        if sha_pinning is False
                        else CheckStatus.UNKNOWN
                    ),
                    confidence=Confidence.HIGH if isinstance(sha_pinning, bool) else Confidence.LOW,
                    reason=(
                        "GitHub requires actions to be pinned to full commit SHAs."
                        if sha_pinning is True
                        else "GitHub does not require full-SHA pinning for actions."
                        if sha_pinning is False
                        else "GitHub did not expose SHA-pinning policy."
                    ),
                    source="github",
                    collected_at=collected_at,
                ),
            ]
        )

    workflow = client.get_workflow_permissions(repository)
    if workflow is None:
        results.append(
            CheckResult(
                check_id="github.actions.default_workflow_permissions",
                title="Default workflow token permissions",
                status=CheckStatus.UNKNOWN,
                confidence=Confidence.LOW,
                reason="Default workflow permissions are not readable with the current token.",
                source="github",
                collected_at=collected_at,
            )
        )
    else:
        default_permissions = workflow.get("default_workflow_permissions")
        can_approve = workflow.get("can_approve_pull_request_reviews")
        least_privilege = default_permissions == "read" and can_approve is False
        results.append(
            CheckResult(
                check_id="github.actions.default_workflow_permissions",
                title="Default workflow token permissions",
                status=CheckStatus.PASS if least_privilege else CheckStatus.FAIL,
                confidence=Confidence.HIGH,
                reason=(
                    "Default workflow permissions are read-only and workflows cannot approve pull requests."
                    if least_privilege
                    else "Default workflow permissions are broader than the project's least-privilege baseline."
                ),
                source="github",
                collected_at=collected_at,
                metadata={
                    "default_workflow_permissions": default_permissions,
                    "can_approve_pull_request_reviews": can_approve,
                },
            )
        )

    return results
