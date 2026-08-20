# v0.1.0 Release Checklist

This checklist defines the release gate for Security Evidence Collector v0.1.0. New product features are out of scope until these gates are closed.

## Core

- [x] GitHub collector produces normalized evidence.
- [x] Findings use explicit PASS / FAIL / UNKNOWN / NOT_APPLICABLE / ERROR states.
- [x] Evidence Pack generation is implemented.
- [x] SHA-256 manifest verification is implemented.
- [x] Internal control mappings and ISO/IEC 27001:2022 / NIS2 supporting references are separated from compliance determinations.
- [x] Evidence Contract v1 is versioned and documented.
- [x] Stable `evidence_id`, source/collector metadata and scope references are available.
- [x] Freshness and validity metadata are represented without making assurance decisions.
- [x] Formal JSON Schema exists for downstream consumers.

## Quality and security

- [x] Ruff linting configured.
- [x] Strict Mypy configured.
- [x] pytest configured for supported Python versions.
- [x] Minimum coverage gate configured.
- [x] Bandit configured.
- [x] pip-audit configured.
- [x] SECURITY.md present.
- [x] No runtime LLM dependency.
- [x] Credentials are not written to Evidence Packs.
- [x] CI and Security workflows were green on the release-candidate implementation head before checklist synchronization.

## Automation

- [x] Self-assessment Evidence Automation exists.
- [x] Evidence Pack verification occurs before artifact upload.
- [x] Weekly schedule and workflow_dispatch are available.
- [x] External repository smoke-test workflow exists.
- [ ] External smoke matrix passes for pallets/flask, fastapi/fastapi and psf/requests.

## Demo and documentation

- [x] GitHub Pages source exists under docs/.
- [x] Public Quick Scan is documented as a limited public-data view.
- [x] Sanitized demo Evidence Pack exists.
- [x] README includes Quick Start, architecture, checks, security model and disclaimer.
- [x] CHANGELOG.md exists.
- [x] Apache-2.0 licensing is declared.
- [ ] GitHub Pages deployment confirmed reachable.

## Release

- [x] Package version set to 0.1.0.
- [x] README marks v0.1.0 release candidate state.
- [x] v0.1.0 changelog prepared.
- [ ] All release workflows green on the final release commit.
- [ ] Tag v0.1.0 created.
- [ ] GitHub Release v0.1.0 published.

## Release rule

Do not add AWS, Azure, Linux, Jira, ServiceNow or other new collectors before v0.1.0 is released. Those belong to subsequent versions.
