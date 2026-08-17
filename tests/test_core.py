from datetime import datetime, timezone

from sec_evidence.integrity import sha256_file
from sec_evidence.models import CheckResult, CheckStatus, Confidence


def test_check_result_accepts_utc_timestamp() -> None:
    result = CheckResult(
        check_id="github.repository.visibility",
        title="Repository visibility",
        status=CheckStatus.PASS,
        confidence=Confidence.HIGH,
        reason="Visibility was returned directly by the provider API.",
        source="github",
        collected_at=datetime.now(timezone.utc),
    )
    assert result.status is CheckStatus.PASS


def test_sha256_file(tmp_path) -> None:
    sample = tmp_path / "evidence.txt"
    sample.write_text("evidence", encoding="utf-8")
    assert sha256_file(sample) == "1f7f974adf7bf0a58e1e3d7437a343b69e7061d17ca8b7d4cc3f8b41c36c7c9e"
