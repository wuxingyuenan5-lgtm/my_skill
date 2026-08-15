from __future__ import annotations

from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class HealthRecord:
    status: str = "healthy"
    consecutive_failures: int = 0
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    failure_reason: Optional[str] = None


class SourceHealthTracker:
    """In-memory source health tracker.

    v0.1.0 deliberately avoids persistence: health is process-local evidence, while
    durable source status belongs in the reviewed source registry/reference docs.
    """

    def __init__(self) -> None:
        self._records: dict[str, HealthRecord] = {}

    def get(self, source_id: str) -> HealthRecord:
        return self._records.setdefault(source_id, HealthRecord())

    def status(self, source_id: str) -> str:
        return self.get(source_id).status

    def record_success(self, source_id: str, at: Optional[str] = None) -> HealthRecord:
        rec = self.get(source_id)
        rec.consecutive_failures = 0
        rec.status = "healthy"
        rec.last_success = at or datetime.now(timezone.utc).isoformat()
        rec.failure_reason = None
        return rec

    def record_failure(self, source_id: str, reason: str, at: Optional[str] = None) -> HealthRecord:
        rec = self.get(source_id)
        rec.consecutive_failures += 1
        rec.last_failure = at or datetime.now(timezone.utc).isoformat()
        rec.failure_reason = reason
        rec.status = "broken" if rec.consecutive_failures >= 3 else "degraded"
        return rec
