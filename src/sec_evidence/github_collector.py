"""GitHub repository evidence collector."""

from __future__ import annotations

from datetime import datetime, timezone

from sec_evidence.github_client import GitHubClient
from sec_evidence.github_security_checks import collect_devsecops_checks
from sec_evidence.models import CheckResult, CheckStatus, Confidence

SECURITY_POLICY_PATHS = ("SECURITY.md", ".github/SECURITY.md", "docs/SECURITY.md")
CODEOWNERS_PATHS = ("CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS")


def _file_presence_result(
    repository: str,
    client: GitHubClient,
    *,
    check_id: str,
    title: str,
    paths: tuple[str, ...],
    collected_at: datetime,
) -> CheckResult:
    for path in paths:
        if client.content_exists(repository, path):
            return CheckResult(
                check_id=check_id,
                title=title,
                status=CheckStatus.PASS,
                confidence=Confidence.HIGH,
                reason=f"GitHub repository contains '{path}'.",
                source="github",
                collected_at=collected_at,
                metadata={"path": path},
            )
    return CheckResult(
        check_id=check_id,
        title=title,
        status=CheckStatus.FAIL,
        confidence=Confidence.HIGH,
        reason=f"None of the recognized paths were found: {', '.join(paths)}.",
        source="github",
        collected_at=collected_at,
        metadata={"paths_checked": ",".join(paths)},
    )


def collect_repository_metadata(repository: str, client: GitHubClient) -> list[CheckResult]:
    """Collect deterministic repository metadata, governance and DevSecOps checks."""
    payload = client.get_repository(repository)
    collected_at = datetime.now(timezone.utc)

    visibility = payload.get("visibility")
    default_branch = payload.get("default_branch")
    archived = payload.get("archived")

    results = [
        CheckResult(
            check_id="github.repository.visibility",
            title="Repository visibility",
            status=CheckStatus.PASS if visibility else CheckStatus.UNKNOWN,
            confidence=Confidence.HIGH if visibility else Confidence.LOW,
            reason=(
                f"GitHub API reported repository visibility as '{visibility}'."
                if visibility
                else "GitHub API did not return repository visibility."
            ),
            source="github",
            collected_at=collected_at,
            metadata={"visibility": visibility},
        ),
        CheckResult(
            check_id="github.repository.default_branch",
            title="Default branch identified",
            status=CheckStatus.PASS if default_branch else CheckStatus.UNKNOWN,
            confidence=Confidence.HIGH if default_branch else Confidence.LOW,
            reason=(
                f"GitHub API reported default branch '{default_branch}'."
                if default_branch
                else "GitHub API did not return a default branch."
            ),
            source="github",
            collected_at=collected_at,
            metadata={"default_branch": default_branch},
        ),
        CheckResult(
            check_id="github.repository.archived",
            title="Repository is active",
            status=(
                CheckStatus.FAIL
                if archived is True
                else CheckStatus.PASS
                if archived is False
                else CheckStatus.UNKNOWN
            ),
            confidence=Confidence.HIGH if isinstance(archived, bool) else Confidence.LOW,
            reason=(
                "GitHub API reported that the repository is archived."
                if archived is True
                else "GitHub API reported that the repository is not archived."
                if archived is False
                else "GitHub API did not return archived status."
            ),
            source="github",
            collected_at=collected_at,
            metadata={"archived": archived},
        ),
        _file_presence_result(
            repository,
            client,
            check_id="github.governance.security_policy",
            title="Security policy present",
            paths=SECURITY_POLICY_PATHS,
            collected_at=collected_at,
        ),
        _file_presence_result(
            repository,
            client,
            check_id="github.governance.codeowners",
            title="CODEOWNERS present",
            paths=CODEOWNERS_PATHS,
            collected_at=collected_at,
        ),
    ]

    results.extend(collect_devsecops_checks(repository, payload, client, collected_at))

    if isinstance(default_branch, str) and default_branch:
        protection = client.get_branch_protection(repository, default_branch)
        if protection is None:
            results.extend(
                [
                    CheckResult(
                        check_id="github.branch.protection",
                        title="Default branch protection",
                        status=CheckStatus.UNKNOWN,
                        confidence=Confidence.LOW,
                        reason=(
                            "GitHub returned 404 for branch protection. This can mean the branch "
                            "is unprotected or that the token cannot inspect protection settings."
                        ),
                        source="github",
                        collected_at=collected_at,
                        metadata={"branch": default_branch},
                    ),
                    CheckResult(
                        check_id="github.branch.required_reviews",
                        title="Required pull-request reviews",
                        status=CheckStatus.UNKNOWN,
                        confidence=Confidence.LOW,
                        reason="Branch protection details were not available.",
                        source="github",
                        collected_at=collected_at,
                        metadata={"branch": default_branch},
                    ),
                    CheckResult(
                        check_id="github.branch.required_status_checks",
                        title="Required status checks",
                        status=CheckStatus.UNKNOWN,
                        confidence=Confidence.LOW,
                        reason="Branch protection details were not available.",
                        source="github",
                        collected_at=collected_at,
                        metadata={"branch": default_branch},
                    ),
                ]
            )
        else:
            reviews = protection.get("required_pull_request_reviews")
            status_checks = protection.get("required_status_checks")
            results.extend(
                [
                    CheckResult(
                        check_id="github.branch.protection",
                        title="Default branch protection",
                        status=CheckStatus.PASS,
                        confidence=Confidence.HIGH,
                        reason="GitHub API returned branch protection configuration.",
                        source="github",
                        collected_at=collected_at,
                        metadata={"branch": default_branch},
                    ),
                    CheckResult(
                        check_id="github.branch.required_reviews",
                        title="Required pull-request reviews",
                        status=CheckStatus.PASS if reviews else CheckStatus.FAIL,
                        confidence=Confidence.HIGH,
                        reason=(
                            "Required pull-request reviews are configured."
                            if reviews
                            else "Branch protection is present but required reviews are not configured."
                        ),
                        source="github",
                        collected_at=collected_at,
                        metadata={"branch": default_branch},
                    ),
                    CheckResult(
                        check_id="github.branch.required_status_checks",
                        title="Required status checks",
                        status=CheckStatus.PASS if status_checks else CheckStatus.FAIL,
                        confidence=Confidence.HIGH,
                        reason=(
                            "Required status checks are configured."
                            if status_checks
                            else "Branch protection is present but required status checks are not configured."
                        ),
                        source="github",
                        collected_at=collected_at,
                        metadata={"branch": default_branch},
                    ),
                ]
            )

    return results
