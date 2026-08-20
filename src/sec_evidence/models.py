"""Core deterministic result models and versioned evidence contracts."""

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator

EVIDENCE_SCHEMA_VERSION = "1.0"


class CheckStatus(StrEnum):
    PASS = "PASS"  # nosec B105 -- deterministic check state, not a credential
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    ERROR = "ERROR"


class Confidence(StrEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Severity(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class EvidenceFreshness(StrEnum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    UNKNOWN = "UNKNOWN"


class EvidenceScope(BaseModel):
    """Optional scope metadata used by downstream assurance workflows."""

    organization_id: str | None = None
    asset_id: str | None = None
    service_id: str | None = None
    owner: str | None = None
    collection_scope: str | None = None


class EvidenceMetadata(BaseModel):
    """Machine-readable metadata that makes evidence portable across products."""

    schema_version: str = EVIDENCE_SCHEMA_VERSION
    evidence_id: str | None = None
    evidence_type: str | None = None
    source_system: str | None = None
    source_version: str | None = None
    collector_version: str | None = None
    content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    freshness: EvidenceFreshness = EvidenceFreshness.UNKNOWN
    scope: EvidenceScope = Field(default_factory=EvidenceScope)

    @field_validator("valid_from", "valid_until")
    @classmethod
    def normalize_optional_utc(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("evidence validity timestamps must be timezone-aware")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def validate_validity_interval(self) -> "EvidenceMetadata":
        if self.valid_from is not None and self.valid_until is not None:
            if self.valid_until < self.valid_from:
                raise ValueError("valid_until must be greater than or equal to valid_from")
        return self


class CheckResult(BaseModel):
    """Normalized result produced by one deterministic security check."""

    check_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    status: CheckStatus
    confidence: Confidence
    reason: str = Field(min_length=1)
    source: str = Field(min_length=1)
    collected_at: datetime
    raw_evidence_reference: str | None = None
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
    evidence: EvidenceMetadata = Field(default_factory=EvidenceMetadata)

    @field_validator("collected_at")
    @classmethod
    def require_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("collected_at must be timezone-aware")
        return value.astimezone(timezone.utc)
