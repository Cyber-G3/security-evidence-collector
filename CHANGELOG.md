# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-08-18

### Added

- GitHub repository metadata and governance checks.
- `SECURITY.md` and `CODEOWNERS` presence checks.
- Branch protection, required review, and required status-check inspection when readable.
- Dependabot configuration and selected GitHub security feature checks.
- GitHub Actions policy, SHA-pinning and workflow-permission checks when readable.
- Deterministic `PASS`, `FAIL`, `UNKNOWN`, `NOT_APPLICABLE`, and `ERROR` result states.
- Structured Evidence Packs with normalized evidence, findings, internal-control mappings, framework references and Markdown reports.
- SHA-256 manifest generation and integrity verification.
- Curated supporting references for ISO/IEC 27001:2022 and NIS2 without compliance-determination claims.
- Scheduled and manual GitHub Actions evidence automation.
- End-to-end self-test that generates, verifies and uploads an Evidence Pack artifact.
- Public GitHub Pages landing page with a token-free Public Quick Scan for public repositories.
- Sanitized demo Evidence Pack under `examples/demo-evidence-pack/`.
- CI gates for Ruff, strict Mypy, pytest on Python 3.12/3.13 and minimum 80% coverage.
- Security gates for Bandit and `pip-audit`.

### Changed

- Permission-restricted GitHub settings are classified as `UNKNOWN` instead of aborting evidence collection.
- Evidence automation self-tests on relevant collector and workflow changes.

### Security

- Runtime credentials are read from environment variables or GitHub Actions secrets and are not written to Evidence Packs.
- The collector is designed for read-only source-system access.

### Notes

This release supports evidence collection and control analysis. Framework references do not constitute certification, regulatory compliance, legal advice, or audit assurance.
