from datetime import datetime, timezone

from sec_evidence.control_mapping import load_check_mappings
from sec_evidence.findings import build_findings
from sec_evidence.models import CheckResult, CheckStatus, Confidence


def _result(check_id: str, status: CheckStatus) -> CheckResult:
    return CheckResult(
        check_id=check_id,
        title=check_id,
        status=status,
        confidence=Confidence.HIGH,
        reason="deterministic test result",
        source="github",
        collected_at=datetime(2026, 8, 17, tzinfo=timezone.utc),
    )


def test_mapping_loads_packaged_yaml() -> None:
    mappings = load_check_mappings()
    assert mappings["github.branch.required_reviews"] == ["SEC-SDLC-003"]


def test_fail_creates_documented_finding() -> None:
    findings = build_findings(
        [_result("github.branch.required_reviews", CheckStatus.FAIL)],
        load_check_mappings(),
    )
    assert len(findings) == 1
    assert findings[0]["severity"] == "HIGH"
    assert findings[0]["control_ids"] == ["SEC-SDLC-003"]


def test_unknown_does_not_create_failure_finding() -> None:
    findings = build_findings(
        [_result("github.branch.required_reviews", CheckStatus.UNKNOWN)],
        load_check_mappings(),
    )
    assert findings == []
