# Evidence Contract v1

This document defines the portable metadata contract for normalized evidence produced by Security Evidence Collector.

## Goals

- keep collection deterministic, local-first and read-only;
- make evidence portable across CLI, API and future platform consumers;
- preserve provenance, identity and collection context;
- support freshness and validity decisions without making compliance determinations;
- support integrity verification without turning the collector into an assurance engine;
- keep tenancy, remediation and AI assurance outside the collector boundary.

## Contract

Each normalized check retains the existing deterministic fields and includes an `evidence` object.

```json
{
  "check_id": "github.branch.protection",
  "title": "Default branch protection",
  "status": "PASS",
  "confidence": "HIGH",
  "reason": "Branch protection is enabled",
  "source": "github",
  "collected_at": "2026-08-20T07:00:00Z",
  "raw_evidence_reference": "normalized/github/branch-protection.json",
  "metadata": {},
  "evidence": {
    "schema_version": "1.0",
    "evidence_id": "github:Cyber-G3/example:github.branch.protection",
    "evidence_type": "configuration",
    "source_system": "github",
    "source_version": "rest-api-v3",
    "collector_version": "0.1.0",
    "content_sha256": null,
    "valid_from": null,
    "valid_until": null,
    "freshness": "UNKNOWN",
    "scope": {
      "organization_id": "Cyber-G3",
      "asset_id": "Cyber-G3/example",
      "service_id": null,
      "owner": null,
      "collection_scope": "repository"
    }
  }
}
```

## Fields

- `schema_version`: evidence contract version, independent from package version.
- `evidence_id`: stable external identifier for a normalized evidence observation. GitHub evidence uses `github:{repository}:{check_id}`.
- `evidence_type`: normalized evidence category such as `configuration`, `document`, `log`, `scan`, or `attestation`.
- `source_system`: originating system.
- `source_version`: optional source/product/API version when available.
- `collector_version`: collector version that generated the record.
- `content_sha256`: optional lowercase SHA-256 digest for evidence content when a content-level digest is available. Evidence Pack integrity remains independently protected by the pack manifest.
- `valid_from` / `valid_until`: optional timezone-aware validity interval. If both exist, `valid_until` cannot precede `valid_from`.
- `freshness`: `CURRENT`, `STALE`, `EXPIRED`, or `UNKNOWN`.
- `scope.organization_id`: optional external organization reference.
- `scope.asset_id`: optional asset reference.
- `scope.service_id`: optional critical/business service reference.
- `scope.owner`: optional evidence owner.
- `scope.collection_scope`: human-readable collection boundary, e.g. repository, organization, host, tenant.

## Identity and integrity

`evidence_id` provides stable identity for downstream correlation. It is not a cryptographic digest and must not be used as an integrity check.

`content_sha256` is reserved for a digest of the relevant evidence content when one is available. The Evidence Pack manifest remains the authoritative pack-level integrity mechanism and detects modified serialized artifacts.

## Boundary

The collector does not decide whether evidence is sufficient for certification or regulatory compliance. Downstream assurance workflows may use this metadata to evaluate recency, scope, provenance and integrity with human review.

The collector also does not assign tenants, create remediation actions, make legal conclusions or use an LLM to determine compliance status.

## Compatibility

The `evidence` object and its new fields have defaults, so existing callers that construct `CheckResult` without them remain compatible. Consumers should persist `schema_version`, `evidence_id`, `collector_version` and source context when exchanging normalized evidence.
