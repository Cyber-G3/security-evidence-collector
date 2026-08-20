from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from sec_evidence.models import (
    CheckResult,
    CheckStatus,
    Confidence,
    EvidenceFreshness,
    EvidenceMetadata,
    EvidenceScope,
)


def test_check_result_keeps_backward_compatible_defaults() -> None:
    result = CheckResult(
        check_id="example",
        title="Example check",
        status=CheckStatus.PASS,
        confidence=Confidence.HIGH,
        reason="ok",
        source="test",
        collected_at=datetime.now(timezone.utc),
    )

    assert result.evidence.schema_version == "1.0"
    assert result.evidence.freshness == EvidenceFreshness.UNKNOWN
    assert result.evidence.scope == EvidenceScope()


def test_evidence_metadata_normalizes_validity_to_utc() -> None:
    metadata = EvidenceMetadata(
        valid_from=datetime(2026, 8, 20, 9, 0, tzinfo=timezone.utc),
        valid_until=datetime(2026, 9, 20, 9, 0, tzinfo=timezone.utc),
        freshness=EvidenceFreshness.CURRENT,
        scope=EvidenceScope(asset_id="asset-1", service_id="service-1"),
    )

    assert metadata.valid_from is not None
    assert metadata.valid_from.utcoffset().total_seconds() == 0
    assert metadata.scope.asset_id == "asset-1"


def test_evidence_validity_requires_timezone() -> None:
    with pytest.raises(ValidationError):
        EvidenceMetadata(valid_until=datetime(2026, 9, 20, 9, 0))
