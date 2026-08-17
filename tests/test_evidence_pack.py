from datetime import datetime, timezone

from sec_evidence.evidence_pack import create_evidence_pack, verify_evidence_pack
from sec_evidence.models import CheckResult, CheckStatus, Confidence


def _result() -> CheckResult:
    return CheckResult(
        check_id="github.repository.visibility",
        title="Repository visibility",
        status=CheckStatus.PASS,
        confidence=Confidence.HIGH,
        reason="GitHub API reported public visibility.",
        source="github",
        collected_at=datetime(2026, 8, 17, tzinfo=timezone.utc),
    )


def test_create_and_verify_evidence_pack(tmp_path) -> None:
    pack = create_evidence_pack("Cyber-G3/example", [_result()], tmp_path)
    assert (pack / "metadata.json").is_file()
    assert (pack / "manifest.json").is_file()
    assert (pack / "reports" / "report.md").is_file()
    valid, messages = verify_evidence_pack(pack)
    assert valid is True
    assert messages


def test_verify_detects_modified_evidence(tmp_path) -> None:
    pack = create_evidence_pack("Cyber-G3/example", [_result()], tmp_path)
    evidence = next((pack / "normalized" / "github").glob("*.json"))
    evidence.write_text("tampered", encoding="utf-8")
    valid, messages = verify_evidence_pack(pack)
    assert valid is False
    assert any(message.startswith("MODIFIED") for message in messages)
