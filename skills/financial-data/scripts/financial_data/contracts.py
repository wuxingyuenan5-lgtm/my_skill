from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional


class ErrorCode(str, Enum):
    INSTRUMENT_NOT_FOUND = "INSTRUMENT_NOT_FOUND"
    FIELD_NOT_SUPPORTED = "FIELD_NOT_SUPPORTED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    SOURCE_BLOCKED = "SOURCE_BLOCKED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    RATE_LIMITED = "RATE_LIMITED"
    STALE_DATA = "STALE_DATA"
    NORMALIZATION_ERROR = "NORMALIZATION_ERROR"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    SOURCE_CONFLICT = "SOURCE_CONFLICT"
    COMPLIANCE_RESTRICTED = "COMPLIANCE_RESTRICTED"


class QualityFlag(str, Enum):
    STALE_DATA = "STALE_DATA"
    SOURCE_CONFLICT = "SOURCE_CONFLICT"
    PARTIAL_DATA = "PARTIAL_DATA"
    UNIT_MISMATCH = "UNIT_MISMATCH"
    CURRENCY_MISMATCH = "CURRENCY_MISMATCH"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    FALLBACK_USED = "FALLBACK_USED"
    UNVERIFIED = "UNVERIFIED"


class FinancialDataError(Exception):
    def __init__(self, code: ErrorCode, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code.value, "message": self.message, "details": self.details}


@dataclass(frozen=True)
class DataRequest:
    instrument: str
    field: str
    market: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    as_of: Optional[str] = None
    output_profile: str = "standard"
    require_crosscheck: bool = False
    debug: bool = False
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.output_profile not in {"compact", "standard", "full"}:
            raise ValueError("output_profile must be compact, standard, or full")
        if not self.instrument:
            raise ValueError("instrument is required")
        if not self.field:
            raise ValueError("field is required")


@dataclass
class DataPoint:
    instrument_id: str
    symbol: str
    field: str
    value: Any
    unit: str
    as_of: str
    retrieved_at: str
    source_id: str
    source_type: str
    currency: Optional[str] = None
    trade_date: Optional[str] = None
    calendar_date: Optional[str] = None
    report_period: Optional[str] = None
    publish_date: Optional[str] = None
    adjustment: Optional[str] = None
    status: str = "unverified"
    quality_flags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    derived_from: list[str] = field(default_factory=list)
    algorithm_version: Optional[str] = None
    parameters: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        required = {
            "instrument_id": self.instrument_id,
            "symbol": self.symbol,
            "field": self.field,
            "unit": self.unit,
            "as_of": self.as_of,
            "retrieved_at": self.retrieved_at,
            "source_id": self.source_id,
            "source_type": self.source_type,
        }
        missing = [name for name, value in required.items() if value in (None, "")]
        if missing:
            raise ValueError(f"missing required provenance fields: {', '.join(missing)}")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["quality_flags"] = [f.value if isinstance(f, Enum) else f for f in self.quality_flags]
        return payload


@dataclass
class DataResult:
    data: list[DataPoint] = field(default_factory=list)
    errors: list[FinancialDataError] = field(default_factory=list)
    sources_used: list[str] = field(default_factory=list)
    fallbacks_used: list[dict[str, str]] = field(default_factory=list)
    status: str = "ok"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "data": [p.to_dict() for p in self.data],
            "errors": [e.to_dict() for e in self.errors],
            "sources_used": list(self.sources_used),
            "fallbacks_used": list(self.fallbacks_used),
            "metadata": dict(self.metadata),
        }
