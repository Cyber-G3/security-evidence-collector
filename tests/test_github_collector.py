import httpx
import respx

from sec_evidence.github_client import GITHUB_API_URL, GitHubClient
from sec_evidence.github_collector import collect_repository_metadata
from sec_evidence.models import CheckStatus


def _status_map(results):
    return {result.check_id: result.status for result in results}


@respx.mock
def test_governance_checks_with_branch_protection() -> None:
    repository = "example/project"
    respx.get(f"{GITHUB_API_URL}/repos/example/project").mock(
        return_value=httpx.Response(
            200,
            json={"visibility": "public", "default_branch": "main", "archived": False},
        )
    )
    respx.get(f"{GITHUB_API_URL}/repos/example/project/contents/SECURITY.md").mock(
        return_value=httpx.Response(200, json={"type": "file"})
    )
    respx.get(f"{GITHUB_API_URL}/repos/example/project/contents/CODEOWNERS").mock(
        return_value=httpx.Response(200, json={"type": "file"})
    )
    respx.get(f"{GITHUB_API_URL}/repos/example/project/branches/main/protection").mock(
        return_value=httpx.Response(
            200,
            json={
                "required_pull_request_reviews": {"required_approving_review_count": 1},
                "required_status_checks": {"strict": True, "contexts": ["test"]},
            },
        )
    )

    with GitHubClient(token="test-token") as client:
        statuses = _status_map(collect_repository_metadata(repository, client))

    assert statuses["github.governance.security_policy"] is CheckStatus.PASS
    assert statuses["github.governance.codeowners"] is CheckStatus.PASS
    assert statuses["github.branch.protection"] is CheckStatus.PASS
    assert statuses["github.branch.required_reviews"] is CheckStatus.PASS
    assert statuses["github.branch.required_status_checks"] is CheckStatus.PASS


@respx.mock
def test_branch_protection_404_is_unknown_not_fail() -> None:
    repository = "example/project"
    respx.get(f"{GITHUB_API_URL}/repos/example/project").mock(
        return_value=httpx.Response(
            200,
            json={"visibility": "public", "default_branch": "main", "archived": False},
        )
    )
    for path in (
        "SECURITY.md",
        ".github/SECURITY.md",
        "docs/SECURITY.md",
        "CODEOWNERS",
        ".github/CODEOWNERS",
        "docs/CODEOWNERS",
    ):
        respx.get(f"{GITHUB_API_URL}/repos/example/project/contents/{path}").mock(
            return_value=httpx.Response(404)
        )
    respx.get(f"{GITHUB_API_URL}/repos/example/project/branches/main/protection").mock(
        return_value=httpx.Response(404)
    )

    with GitHubClient(token="test-token") as client:
        statuses = _status_map(collect_repository_metadata(repository, client))

    assert statuses["github.governance.security_policy"] is CheckStatus.FAIL
    assert statuses["github.governance.codeowners"] is CheckStatus.FAIL
    assert statuses["github.branch.protection"] is CheckStatus.UNKNOWN
    assert statuses["github.branch.required_reviews"] is CheckStatus.UNKNOWN
    assert statuses["github.branch.required_status_checks"] is CheckStatus.UNKNOWN
