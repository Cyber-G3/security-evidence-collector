import httpx
import pytest
import respx

from sec_evidence.exceptions import ApiError, AuthenticationError
from sec_evidence.github_client import GITHUB_API_URL, GitHubClient


@respx.mock
def test_get_repository_metadata() -> None:
    route = respx.get(f"{GITHUB_API_URL}/repos/Cyber-G3/security-evidence-collector").mock(
        return_value=httpx.Response(
            200,
            json={"visibility": "public", "default_branch": "main", "archived": False},
        )
    )
    with GitHubClient(token="test-token") as client:
        payload = client.get_repository("Cyber-G3/security-evidence-collector")
    assert route.called
    assert payload["visibility"] == "public"


@respx.mock
def test_repository_not_found_is_handled() -> None:
    respx.get(f"{GITHUB_API_URL}/repos/example/missing").mock(
        return_value=httpx.Response(404, json={"message": "Not Found"})
    )
    with GitHubClient(token="test-token") as client, pytest.raises(ApiError, match="not found"):
        client.get_repository("example/missing")


@respx.mock
def test_authentication_failure_is_explicit() -> None:
    respx.get(f"{GITHUB_API_URL}/repos/example/private").mock(return_value=httpx.Response(401))
    with GitHubClient(token="bad-token") as client, pytest.raises(AuthenticationError):
        client.get_repository("example/private")


@respx.mock
def test_rate_limit_failure_is_explicit() -> None:
    respx.get(f"{GITHUB_API_URL}/repos/example/project").mock(
        return_value=httpx.Response(
            403,
            headers={"x-ratelimit-remaining": "0", "x-ratelimit-reset": "123456"},
        )
    )
    with GitHubClient(token="test-token") as client, pytest.raises(ApiError, match="rate limit"):
        client.get_repository("example/project")


@respx.mock
def test_actions_permissions_403_becomes_unknown_capability() -> None:
    respx.get(f"{GITHUB_API_URL}/repos/example/project/actions/permissions").mock(
        return_value=httpx.Response(403)
    )
    with GitHubClient(token="test-token") as client:
        assert client.get_actions_permissions("example/project") is None


@respx.mock
def test_workflow_permissions_are_returned_when_readable() -> None:
    respx.get(f"{GITHUB_API_URL}/repos/example/project/actions/permissions/workflow").mock(
        return_value=httpx.Response(
            200,
            json={
                "default_workflow_permissions": "read",
                "can_approve_pull_request_reviews": False,
            },
        )
    )
    with GitHubClient(token="test-token") as client:
        payload = client.get_workflow_permissions("example/project")
    assert payload is not None
    assert payload["default_workflow_permissions"] == "read"


def test_invalid_repository_format_is_rejected() -> None:
    with GitHubClient(token="test-token") as client, pytest.raises(ValueError, match="OWNER/REPO"):
        client.get_repository("invalid")
