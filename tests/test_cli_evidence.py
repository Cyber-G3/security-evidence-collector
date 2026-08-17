from pathlib import Path

from typer.testing import CliRunner

from sec_evidence.cli import app
from sec_evidence.evidence_pack import create_evidence_pack
from sec_evidence.models import CheckResult, CheckStatus, Confidence
from datetime import datetime, timezone

runner = CliRunner()


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


def test_verify_command_passes_for_valid_pack(tmp_path: Path) -> None:
    pack = create_evidence_pack("Cyber-G3/example", [_result()], tmp_path)
    result = runner.invoke(app, ["verify", str(pack)])
    assert result.exit_code == 0
    assert "PASSED" in result.stdout


def test_verify_command_fails_for_tampered_pack(tmp_path: Path) -> None:
    pack = create_evidence_pack("Cyber-G3/example", [_result()], tmp_path)
    evidence = next((pack / "normalized" / "github").glob("*.json"))
    evidence.write_text("tampered", encoding="utf-8")
    result = runner.invoke(app, ["verify", str(pack)])
    assert result.exit_code == 5
    assert "MODIFIED" in result.stdout
