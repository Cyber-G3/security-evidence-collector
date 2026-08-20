# Evidence Contract v1

This document defines the portable metadata contract for normalized evidence produced by Security Evidence Collector.

## Goals

- keep collection deterministic, local-first and read-only;
- make evidence portable across CLI, API and future platform consumers;
- preserve provenance and collection context;
- support freshness and validity decisions without making compliance determinations;
- keep tenancy, remediation and AI assurance outside the collector boundary.

## Contract

Each normalized check retains the existing deterministic fields and now includes an `evidence` object.

```json
{
  "check_id": "github.branch_protection",
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
    "evidence_type": "configuration",
    "source_system": "github",
    "source_version": null,
    "collector_version": "0.1.0",
    "valid_from": null,
    "valid_until": null,
    "freshness": "UNKNOWN",
    "scope": {
      "organization_id": null,
      "asset_id": null,
      "service_id": null,
      "owner": null,
      "collection_scope": "repository"
    }
  }
}
```

## Fields

- `schema_version`: evidence contract version, independent from package version.
- `evidence_type`: normalized evidence category such as `configuration`, `policy`, `log`, `scan`, or `attestation`.
- `source_system`: originating system.
- `source_version`: optional source/product/API version when available.
- `collector_version`: collector version that generated the record.
- `valid_from` / `valid_until`: optional timezone-aware validity interval.
- `freshness`: `CURRENT`, `STALE`, `EXPIRED`, or `UNKNOWN`.
- `scope.organization_id`: optional external organization reference.
- `scope.asset_id`: optional asset reference.
- `scope.service_id`: optional critical/business service reference.
- `scope.owner`: optional evidence owner.
- `scope.collection_scope`: human-readable collection boundary, e.g. repository, organization, host, tenant.

## Boundary

The collector does not decide whether evidence is sufficient for certification or regulatory compliance. Downstream assurance workflows may use this metadata to evaluate recency, scope and provenance with human review.

## Compatibility

The added `evidence` object has defaults, so existing callers that construct `CheckResult` without it remain compatible. Consumers should use `schema_version` when persisting or exchanging normalized evidence.
