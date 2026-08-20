import json
from datetime import datetime, timezone

from sec_evidence.evidence_pack import create_evidence_pack, verify_evidence_pack
from sec_evidence.models import (
    CheckResult,
    CheckStatus,
    Confidence,
    EvidenceMetadata,
    EvidenceScope,
)


def _result() -> CheckResult:
    return CheckResult(
        check_id="github.repository.visibility",
        title="Repository visibility",
        status=CheckStatus.PASS,
        confidence=Confidence.HIGH,
        reason="GitHub API reported public visibility.",
        source="github",
        collected_at=datetime(2026, 8, 17, tzinfo=timezone.utc),
        evidence=EvidenceMetadata(
            evidence_id="github.repository.visibility:Cyber-G3/example",
            evidence_type="configuration",
            source_system="github",
            source_version="rest-api-v3",
            collector_version="0.1.0",
            scope=EvidenceScope(
                organization_id="Cyber-G3",
                asset_id="Cyber-G3/example",
                collection_scope="repository",
            ),
        ),
    )


def test_create_and_verify_evidence_pack(tmp_path) -> None:
    pack = create_evidence_pack("Cyber-G3/example", [_result()], tmp_path)
    assert (pack / "metadata.json").is_file()
    assert (pack / "manifest.json").is_file()
    assert (pack / "reports" / "report.md").is_file()
    valid, messages = verify_evidence_pack(pack)
    assert valid is True
    assert messages


def test_serialized_evidence_pack_preserves_contract_metadata(tmp_path) -> None:
    pack = create_evidence_pack("Cyber-G3/example", [_result()], tmp_path)
    evidence_path = next((pack / "normalized" / "github").glob("*.json"))
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))

    assert payload["evidence"]["schema_version"] == "1.0"
    assert payload["evidence"]["evidence_id"] == "github.repository.visibility:Cyber-G3/example"
    assert payload["evidence"]["evidence_type"] == "configuration"
    assert payload["evidence"]["source_system"] == "github"
    assert payload["evidence"]["source_version"] == "rest-api-v3"
    assert payload["evidence"]["scope"]["organization_id"] == "Cyber-G3"
    assert payload["evidence"]["scope"]["asset_id"] == "Cyber-G3/example"
    assert payload["evidence"]["scope"]["collection_scope"] == "repository"


def test_verify_detects_modified_evidence(tmp_path) -> None:
    pack = create_evidence_pack("Cyber-G3/example", [_result()], tmp_path)
    evidence = next((pack / "normalized" / "github").glob("*.json"))
    evidence.write_text("tampered", encoding="utf-8")
    valid, messages = verify_evidence_pack(pack)
    assert valid is False
    assert any(message.startswith("MODIFIED") for message in messages)
