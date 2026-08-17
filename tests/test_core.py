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
    assert sha256_file(sample) == "ee8250fb76e094b34b471f13a73dbbe51d1ae142e9df59d7c0d31ec20f0a0a8e"
