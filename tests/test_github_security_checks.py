from datetime import datetime, timezone

from sec_evidence.github_security_checks import collect_devsecops_checks
from sec_evidence.models import CheckStatus


class FakeClient:
    def content_exists(self, repository: str, path: str) -> bool:
        return path == ".github/dependabot.yml"

    def get_actions_permissions(self, repository: str):
        return {
            "enabled": True,
            "allowed_actions": "selected",
            "sha_pinning_required": True,
        }

    def get_workflow_permissions(self, repository: str):
        return {
            "default_workflow_permissions": "read",
            "can_approve_pull_request_reviews": False,
        }


class RestrictedClient(FakeClient):
    def get_actions_permissions(self, repository: str):
        return None

    def get_workflow_permissions(self, repository: str):
        return None


def test_devsecops_checks_detect_enabled_features_and_least_privilege() -> None:
    payload = {
        "security_and_analysis": {
            "dependabot_security_updates": {"status": "enabled"},
            "secret_scanning": {"status": "enabled"},
            "secret_scanning_push_protection": {"status": "enabled"},
            "advanced_security": {"status": "enabled"},
        }
    }
    results = collect_devsecops_checks(
        "Cyber-G3/example",
        payload,
        FakeClient(),
        datetime(2026, 8, 17, tzinfo=timezone.utc),
    )
    statuses = {result.check_id: result.status for result in results}
    assert statuses["github.dependencies.dependabot_config"] is CheckStatus.PASS
    assert statuses["github.security.secret_scanning"] is CheckStatus.PASS
    assert statuses["github.security.push_protection"] is CheckStatus.PASS
    assert statuses["github.actions.policy"] is CheckStatus.PASS
    assert statuses["github.actions.sha_pinning"] is CheckStatus.PASS
    assert statuses["github.actions.default_workflow_permissions"] is CheckStatus.PASS


def test_unreadable_actions_administration_is_unknown_not_fail() -> None:
    results = collect_devsecops_checks(
        "Cyber-G3/example",
        {},
        RestrictedClient(),
        datetime(2026, 8, 17, tzinfo=timezone.utc),
    )
    statuses = {result.check_id: result.status for result in results}
    assert statuses["github.actions.policy"] is CheckStatus.UNKNOWN
    assert statuses["github.actions.default_workflow_permissions"] is CheckStatus.UNKNOWN
    assert statuses["github.security.secret_scanning"] is CheckStatus.UNKNOWN
