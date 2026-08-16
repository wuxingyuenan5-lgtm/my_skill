from __future__ import annotations

from typing import Optional
from .contracts import DataRequest
from .instruments import Instrument
from .registry import SourceRegistry, SourceSpec
from .source_health import SourceHealthTracker


_GRADE = {"A": 1.0, "B": 0.75, "C": 0.5, "D": 0.25}
_HEALTH = {"healthy": 1.0, "degraded": 0.45, "broken": 0.0, "blocked": 0.0, "deprecated": 0.0}

# Field-level preferences. These are intentionally narrow; all other routing
# falls back to transparent scoring.
_OVERRIDES: dict[tuple[str, str], tuple[str, ...]] = {
    ("US", "filings"): ("sec_edgar",),
    ("US", "fundamentals"): ("sec_edgar", "yahoo"),
    ("US", "xbrl"): ("sec_edgar",),
    ("US", "kline"): ("yahoo", "sina"),
    ("HK", "kline"): ("yahoo", "sina", "tencent"),
    ("US", "yield_curve"): ("treasury",),
    ("US", "yield_2y"): ("treasury",),
    ("US", "yield_10y"): ("treasury",),
    ("US", "spread_10y_2y"): ("treasury",),
    ("GLOBAL", "yield_curve"): ("treasury",),
    ("CN", "quote"): ("tencent", "sina", "eastmoney"),
    ("CN", "price"): ("tencent", "sina", "eastmoney"),
    ("CN", "kline"): ("tencent", "sina"),
    ("CN", "turnover"): ("tencent", "eastmoney"),
    ("CN", "market_cap"): ("tencent", "eastmoney"),
    ("CN", "pe"): ("tencent", "eastmoney"),
    ("CN", "pb"): ("tencent", "eastmoney"),
    ("CN", "filings"): ("cninfo", "sse_szse", "eastmoney"),
}


class Router:
    def __init__(self, registry: SourceRegistry, health_tracker: Optional[SourceHealthTracker] = None):
        self.registry = registry
        self.health_tracker = health_tracker or SourceHealthTracker()

    def route(self, request: DataRequest, instrument: Instrument) -> list[SourceSpec]:
        market = self._market(request, instrument)
        candidates = self.registry.candidates(market, request.field)

        usage = str(request.params.get("usage", "research")).lower()
        if usage == "commercial":
            candidates = [s for s in candidates if s.commercial_use == "allowed"]

        candidates = [s for s in candidates if self._effective_status(s) not in {"broken", "blocked", "deprecated"}]

        preferred = _OVERRIDES.get((market, request.field), ()) or _OVERRIDES.get(("GLOBAL", request.field), ())
        pref_rank = {source_id: i for i, source_id in enumerate(preferred)}

        def key(source: SourceSpec):
            rank = pref_rank.get(source.source_id, len(preferred) + 10)
            return (rank, -self._score(source))

        ordered = sorted(candidates, key=key)
        return self._prefer_independent_fallbacks(ordered)

    def _effective_status(self, source: SourceSpec) -> str:
        runtime = self.health_tracker.status(source.source_id)
        if source.status in {"blocked", "broken", "deprecated"}:
            return source.status
        return runtime if runtime != "healthy" else source.status

    def _score(self, source: SourceSpec) -> float:
        health = _HEALTH.get(self._effective_status(source), 0.25)
        return (
            _GRADE.get(source.authority, 0.25) * 0.30
            + _GRADE.get(source.reliability, 0.25) * 0.25
            + _GRADE.get(source.freshness, 0.25) * 0.20
            + _GRADE.get(source.compliance, 0.25) * 0.15
            + health * 0.10
        )

    @staticmethod
    def _market(request: DataRequest, instrument: Instrument) -> str:
        if request.market:
            market = request.market.upper()
            if market in {"USA", "US"}:
                return "US"
            if market in {"HKG", "HK"}:
                return "HK"
            if market in {"CHINA", "CN", "A"}:
                return "CN"
        return instrument.country.upper()

    @staticmethod
    def _prefer_independent_fallbacks(sources: list[SourceSpec]) -> list[SourceSpec]:
        if len(sources) <= 1:
            return sources
        out: list[SourceSpec] = []
        deferred: list[SourceSpec] = []
        seen_groups: set[str] = set()
        for source in sources:
            if source.independence_group in seen_groups:
                deferred.append(source)
            else:
                out.append(source)
                seen_groups.add(source.independence_group)
        return out + deferred
