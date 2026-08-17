"""Minimal read-only GitHub REST API client."""

from __future__ import annotations

import os
from typing import Any

import httpx

from sec_evidence import __version__
from sec_evidence.exceptions import ApiError, AuthenticationError

GITHUB_API_URL = "https://api.github.com"
GITHUB_API_VERSION = "2026-03-10"


class GitHubClient:
    """Read-only GitHub REST API client used by evidence collectors."""

    def __init__(self, token: str | None = None, timeout: float = 15.0) -> None:
        self._token = token or os.getenv("GITHUB_TOKEN")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
            "User-Agent": f"security-evidence-collector/{__version__}",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        self._client = httpx.Client(
            base_url=GITHUB_API_URL,
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> GitHubClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def get_repository(self, repository: str) -> dict[str, Any]:
        """Return repository metadata from GET /repos/{owner}/{repo}."""
        owner, repo = self._parse_repository(repository)
        response = self._request("GET", f"/repos/{owner}/{repo}")
        payload = response.json()
        if not isinstance(payload, dict):
            raise ApiError("GitHub returned an unexpected repository response.")
        return payload

    def _request(self, method: str, path: str) -> httpx.Response:
        try:
            response = self._client.request(method, path)
        except httpx.TimeoutException as exc:
            raise ApiError("GitHub API request timed out.") from exc
        except httpx.HTTPError as exc:
            raise ApiError("GitHub API request failed.") from exc

        if response.status_code == 401:
            raise AuthenticationError("GitHub authentication failed.")
        if response.status_code == 403:
            remaining = response.headers.get("x-ratelimit-remaining")
            reset = response.headers.get("x-ratelimit-reset")
            if remaining == "0":
                message = "GitHub API rate limit exceeded."
                if reset:
                    message += f" Reset epoch: {reset}."
                raise ApiError(message)
            raise AuthenticationError("GitHub denied access to the requested repository resource.")
        if response.status_code == 404:
            raise ApiError("Repository was not found or is not accessible with the current credentials.")
        if response.status_code >= 400:
            raise ApiError(f"GitHub API returned HTTP {response.status_code}.")

        return response

    @staticmethod
    def _parse_repository(repository: str) -> tuple[str, str]:
        parts = repository.strip().split("/")
        if len(parts) != 2 or not all(parts):
            raise ValueError("Repository must use OWNER/REPO format.")
        return parts[0], parts[1]
