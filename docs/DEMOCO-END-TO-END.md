# DemoCo — End-to-End Evidence Scenario

> Fictional portfolio scenario. No production or customer data is used.

## Situation
DemoCo is preparing an ISO/IEC 27001 and NIS2-oriented assurance review. Management wants evidence that software repositories use appropriate security governance.

## Question
Can DemoCo substantiate repository-security controls with current, traceable technical evidence?

## Workflow
1. Collect repository configuration read-only.
2. Normalize observable security settings.
3. Preserve source and collection timestamp.
4. Generate integrity-verifiable evidence artifacts.
5. Produce deterministic findings.
6. Map findings to internal controls and supporting framework references.
7. Hand evidence to the assurance layer for professional review.

## Example observation
Branch protection cannot be verified because the API token lacks permission.

**Correct result:** `UNKNOWN`.

It must not be converted to `FAIL` merely because evidence was unavailable.

## Assurance implication
The reviewer requests additional evidence or appropriate read-only access. Only after evidence is obtained can design/implementation and operating-effectiveness conclusions be considered.

## Portfolio lesson
The system preserves uncertainty and provenance instead of manufacturing compliance certainty.
