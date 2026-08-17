import httpx
import respx

from sec_evidence.github_client import GITHUB_API_URL, GitHubClient
from sec_evidence.github_collector import collect_repository_metadata
from sec_evidence.models import CheckStatus


@respx.mock
def test_get_repository_metadata() -> None:
    route = respx.get(f"{GITHUB_API_URL}/repos/Cyber-G3/security-evidence-collector").mock(
        return_value=httpx.Response(
            200,
            json={
                "visibility": "public",
                "default_branch": "main",
                "archived": False,
            },
        )
    )

    with GitHubClient(token="test-token") as client:
        payload = client.get_repository("Cyber-G3/security-evidence-collector")

    assert route.called
    assert payload["visibility"] == "public"


@respx.mock
def test_metadata_collector_returns_deterministic_results() -> None:
    respx.get(f"{GITHUB_API_URL}/repos/Cyber-G3/security-evidence-collector").mock(
        return_value=httpx.Response(
            200,
            json={
                "visibility": "public",
                "default_branch": "main",
                "archived": False,
            },
        )
    )

    with GitHubClient(token="test-token") as client:
        results = collect_repository_metadata("Cyber-G3/security-evidence-collector", client)

    assert [result.status for result in results] == [
        CheckStatus.PASS,
        CheckStatus.PASS,
        CheckStatus.PASS,
    ]


@respx.mock
def test_repository_not_found_is_handled() -> None:
    from sec_evidence.exceptions import ApiError

    respx.get(f"{GITHUB_API_URL}/repos/example/missing").mock(
        return_value=httpx.Response(404, json={"message": "Not Found"})
    )

    with GitHubClient(token="test-token") as client:
        try:
            client.get_repository("example/missing")
        except ApiError as exc:
            assert "not found" in str(exc).lower()
        else:
            raise AssertionError("ApiError was not raised")
