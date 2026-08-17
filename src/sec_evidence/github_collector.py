"""GitHub repository metadata evidence collector."""

from __future__ import annotations

from datetime import datetime, timezone

from sec_evidence.github_client import GitHubClient
from sec_evidence.models import CheckResult, CheckStatus, Confidence


def collect_repository_metadata(repository: str, client: GitHubClient) -> list[CheckResult]:
    """Collect deterministic repository metadata checks."""
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
    ]
    return results
