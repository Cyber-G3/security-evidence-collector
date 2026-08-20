import json
from pathlib import Path

from sec_evidence.models import CheckResult, EvidenceMetadata

SCHEMA_PATH = Path("schemas/evidence-contract-v1.schema.json")


def test_versioned_schema_artifact_matches_model_contract() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema["properties"]["evidence"]["properties"]["schema_version"]["const"] == "1.0"
    assert set(schema["properties"]["status"]["enum"]) == {
        "PASS",
        "FAIL",
        "UNKNOWN",
        "NOT_APPLICABLE",
        "ERROR",
    }
    assert set(schema["properties"]["evidence"]["properties"]["freshness"]["enum"]) == {
        "CURRENT",
        "STALE",
        "EXPIRED",
        "UNKNOWN",
    }
    assert schema["properties"]["evidence"]["properties"]["content_sha256"]["pattern"] == "^[0-9a-f]{64}$"

    model_schema = CheckResult.model_json_schema()
    evidence_schema = EvidenceMetadata.model_json_schema()
    assert "evidence" in model_schema["properties"]
    assert "scope" in evidence_schema["properties"]
    assert "evidence_id" in evidence_schema["properties"]
    assert "content_sha256" in evidence_schema["properties"]


def test_schema_artifact_is_valid_json_object() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["type"] == "object"
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
