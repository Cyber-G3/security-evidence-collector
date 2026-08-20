import httpx
import respx

from sec_evidence import __version__
from sec_evidence.github_client import GITHUB_API_URL, GitHubClient
from sec_evidence.github_collector import collect_repository_metadata


@respx.mock
def test_github_results_include_portable_evidence_metadata() -> None:
    repository = "example/project"
    respx.get(f"{GITHUB_API_URL}/repos/{repository}").mock(
        return_value=httpx.Response(
            200,
            json={"visibility": "public", "default_branch": None, "archived": False},
        )
    )
    for path in (
        "SECURITY.md",
        ".github/SECURITY.md",
        "docs/SECURITY.md",
        "CODEOWNERS",
        ".github/CODEOWNERS",
        "docs/CODEOWNERS",
        ".github/dependabot.yml",
    ):
        respx.get(f"{GITHUB_API_URL}/repos/{repository}/contents/{path}").mock(
            return_value=httpx.Response(404)
        )
    respx.get(f"{GITHUB_API_URL}/repos/{repository}/actions/permissions").mock(
        return_value=httpx.Response(403)
    )
    respx.get(f"{GITHUB_API_URL}/repos/{repository}/actions/permissions/workflow").mock(
        return_value=httpx.Response(403)
    )

    with GitHubClient(token="test-token") as client:
        results = collect_repository_metadata(repository, client)

    assert results
    evidence_ids: set[str] = set()
    for result in results:
        assert result.evidence.schema_version == "1.0"
        assert result.evidence.evidence_id == f"github:{repository}:{result.check_id}"
        assert result.evidence.evidence_id not in evidence_ids
        evidence_ids.add(result.evidence.evidence_id)
        assert result.evidence.evidence_type in {"configuration", "document"}
        if result.check_id.startswith("github.governance."):
            assert result.evidence.evidence_type == "document"
        assert result.evidence.source_system == "github"
        assert result.evidence.source_version == "rest-api-v3"
        assert result.evidence.collector_version == __version__
        assert result.evidence.scope.organization_id == "example"
        assert result.evidence.scope.asset_id == repository
        assert result.evidence.scope.collection_scope == "repository"
