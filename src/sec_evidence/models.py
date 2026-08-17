"""Core deterministic result models."""

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


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

    @field_validator("collected_at")
    @classmethod
    def require_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("collected_at must be timezone-aware")
        return value.astimezone(timezone.utc)
