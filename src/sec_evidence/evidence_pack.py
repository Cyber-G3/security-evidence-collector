"""Build local, integrity-verifiable evidence packs."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sec_evidence import __version__
from sec_evidence.integrity import sha256_file
from sec_evidence.models import CheckResult


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def create_evidence_pack(repository: str, results: list[CheckResult], output_root: Path) -> Path:
    """Persist normalized check results and a SHA-256 manifest."""
    collection_id = str(uuid.uuid4())
    pack = output_root / f"evidence-pack-{collection_id}"
    normalized = pack / "normalized" / "github"
    reports = pack / "reports"
    findings = pack / "findings"
    for directory in (normalized, reports, findings):
        directory.mkdir(parents=True, exist_ok=False)

    started = _utc_now()
    _write_json(pack / "metadata.json", {"collection_id": collection_id,"schema_version": "1.0","target": repository,"target_type": "github_repository","tool": "security-evidence-collector","tool_version": __version__,"generated_at": started.isoformat()})

    for result in results:
        safe_id = result.check_id.replace(".", "_")
        _write_json(normalized / f"{safe_id}.json", result.model_dump(mode="json"))

    report_lines = ["# Security Evidence Report","",f"Target: `{repository}`","","| Status | Check | Reason |","|---|---|---|"]
    for result in results:
        reason = result.reason.replace("|", "\\|")
        report_lines.append(f"| {result.status.value} | {result.title} | {reason} |")
    (reports / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    manifest_entries: list[dict[str, object]] = []
    for path in sorted(p for p in pack.rglob("*") if p.is_file() and p.name != "manifest.json"):
        manifest_entries.append({"path": path.relative_to(pack).as_posix(),"sha256": sha256_file(path),"size_bytes": path.stat().st_size})
    _write_json(pack / "manifest.json", {"algorithm": "sha256", "files": manifest_entries})
    return pack


def verify_evidence_pack(pack: Path) -> tuple[bool, list[str]]:
    """Verify files recorded in an evidence-pack manifest."""
    manifest_path = pack / "manifest.json"
    if not manifest_path.is_file():
        return False, ["manifest.json is missing"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    messages: list[str] = []
    valid = True
    for entry in manifest.get("files", []):
        relative = Path(entry["path"])
        target = pack / relative
        if not target.is_file():
            valid = False
            messages.append(f"MISSING {relative.as_posix()}")
            continue
        if sha256_file(target) != entry["sha256"]:
            valid = False
            messages.append(f"MODIFIED {relative.as_posix()}")
        else:
            messages.append(f"PASS {relative.as_posix()}")
    return valid, messages
