# Portfolio Case — Security Evidence Collector

## Problem
Audit and compliance teams repeatedly gather technical evidence from source systems, then manually normalize, validate and map it to controls.

## Solution
A deterministic evidence pipeline that collects read-only security signals, normalizes them, preserves provenance, verifies integrity and produces evidence packs for assurance workflows.

```text
GitHub API
   ↓
Collector
   ↓
Technical checks
   ↓
Normalized evidence
   ├──→ SHA-256 integrity
   ├──→ Findings
   ├──→ Control mappings
   └──→ Reports / Evidence Pack
```

## Engineering evidence
- Python 3.12+
- GitHub REST API
- CLI and GitHub Actions automation
- Ruff + strict Mypy
- pytest with coverage gate
- Bandit + pip-audit
- SHA-256 evidence integrity
- Explicit PASS / FAIL / UNKNOWN / NOT_APPLICABLE / ERROR semantics

## Business outcome
The project reduces repetitive evidence collection and creates a traceable hand-off between security engineering and GRC assurance.

## Next milestone
Expand collectors beyond GitHub while preserving the same evidence contract: local/Linux, vulnerability evidence, Azure and AWS.

## Professional boundary
Technical evidence and mappings support assurance work; they do not establish compliance or certification.
