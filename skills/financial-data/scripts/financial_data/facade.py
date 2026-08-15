from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable, Optional, Union

from .adapters import SecEdgarAdapter, SinaAdapter, TencentAdapter, TreasuryAdapter
from .contracts import DataPoint, DataRequest, DataResult, ErrorCode, FinancialDataError, QualityFlag
from .indicators import market_breadth
from .instruments import Instrument, InstrumentMaster
from .registry import SourceRegistry, default_registry
from .routing import Router
from .source_health import SourceHealthTracker
from .validation import compare_points, compress_result, validate_ohlcv, validate_point


def default_adapters() -> dict[str, Any]:
    return {
        "tencent": TencentAdapter(),
        "sina": SinaAdapter(),
        "sec_edgar": SecEdgarAdapter(),
        "treasury": TreasuryAdapter(),
    }


def _market(request: DataRequest, instrument: Instrument) -> str:
    if request.market:
        m = request.market.upper()
        if m in {"CN", "CHINA", "A"}:
            return "CN"
        if m in {"HK", "HKG"}:
            return "HK"
        if m in {"US", "USA"}:
            return "US"
        return m
    return instrument.country.upper()


def _validate_points(points: list[DataPoint]) -> list[str]:
    errors: list[str] = []
    for point in points:
        errors.extend(validate_point(point))
    by_field = {p.field: p.value for p in points}
    if {"open", "high", "low"}.issubset(by_field) and ("price" in by_field or "close" in by_field):
        row = {
            "open": by_field["open"],
            "high": by_field["high"],
            "low": by_field["low"],
            "close": by_field.get("close", by_field.get("price")),
            "volume": by_field.get("volume"),
            "turnover": by_field.get("turnover"),
        }
        errors.extend(validate_ohlcv(row))
    return errors


def _find_comparable(primary: list[DataPoint], secondary: list[DataPoint]) -> list[tuple[DataPoint, DataPoint]]:
    second_by_field: dict[str, list[DataPoint]] = defaultdict(list)
    for p in secondary:
        second_by_field[p.field].append(p)
    pairs: list[tuple[DataPoint, DataPoint]] = []
    for p in primary:
        candidates = second_by_field.get(p.field, [])
        if candidates:
            pairs.append((p, candidates[0]))
    return pairs


def get_data(
    request: DataRequest,
    *,
    registry: Optional[SourceRegistry] = None,
    adapters: Optional[dict[str, Any]] = None,
    instrument_master: Optional[InstrumentMaster] = None,
    health_tracker: Optional[SourceHealthTracker] = None,
) -> DataResult:
    """Execute the normalized financial-data pipeline.

    The return type is always ``DataResult``. Failures are explicit in ``errors``;
    an empty successful result is never used to mean "source failed".
    """

    registry = registry or default_registry()
    adapters = default_adapters() if adapters is None else adapters
    instrument_master = instrument_master or InstrumentMaster()
    health_tracker = health_tracker or SourceHealthTracker()

    try:
        instrument = instrument_master.resolve(request.instrument, market=request.market)
    except FinancialDataError as exc:
        return DataResult(errors=[exc], status="failed", metadata={"output_profile": request.output_profile})

    market = _market(request, instrument)
    router = Router(registry, health_tracker=health_tracker)
    routes = router.route(request, instrument)
    if not routes:
        raw_candidates = registry.candidates(market, request.field)
        if raw_candidates and str(request.params.get("usage", "research")).lower() == "commercial":
            err = FinancialDataError(
                ErrorCode.COMPLIANCE_RESTRICTED,
                f"No source approved for commercial usage of {request.field} in {market}",
                {"candidate_sources": [s.source_id for s in raw_candidates]},
            )
        else:
            err = FinancialDataError(
                ErrorCode.FIELD_NOT_SUPPORTED,
                f"No registered source supports {request.field} in {market}",
                {"field": request.field, "market": market},
            )
        return DataResult(errors=[err], status="failed", metadata={"output_profile": request.output_profile})

    errors: list[FinancialDataError] = []
    sources_used: list[str] = []
    fallbacks: list[dict[str, str]] = []
    primary_points: Optional[list[DataPoint]] = None
    primary_source: Optional[str] = None
    failed_source: Optional[str] = None

    for source in routes:
        adapter = adapters.get(source.source_id)
        if adapter is None or not getattr(adapter, "supports", lambda *_: False)(request, instrument):
            continue
        try:
            points = adapter.fetch(request, instrument)
            if not points:
                raise FinancialDataError(
                    ErrorCode.SOURCE_UNAVAILABLE,
                    f"{source.source_id} returned an empty dataset",
                    {"source_id": source.source_id, "field": request.field},
                )
            validation_errors = _validate_points(points)
            if validation_errors:
                raise FinancialDataError(
                    ErrorCode.VALIDATION_FAILED,
                    f"{source.source_id} returned data that failed validation",
                    {"source_id": source.source_id, "issues": validation_errors},
                )
            health_tracker.record_success(source.source_id)
            primary_points = points
            primary_source = source.source_id
            sources_used.append(source.source_id)
            if failed_source:
                fallbacks.append({"from": failed_source, "to": source.source_id})
                for p in points:
                    if QualityFlag.FALLBACK_USED.value not in p.quality_flags:
                        p.quality_flags.append(QualityFlag.FALLBACK_USED.value)
            break
        except FinancialDataError as exc:
            errors.append(exc)
            health_tracker.record_failure(source.source_id, exc.message)
            failed_source = source.source_id

    if primary_points is None or primary_source is None:
        if not errors:
            errors.append(
                FinancialDataError(
                    ErrorCode.FIELD_NOT_SUPPORTED,
                    f"Registered sources exist for {request.field}, but no executable v0.1.0 adapter supports it",
                    {"routes": [s.source_id for s in routes]},
                )
            )
        return DataResult(
            errors=errors,
            sources_used=sources_used,
            fallbacks_used=fallbacks,
            status="failed",
            metadata={"instrument": instrument.ticker, "output_profile": request.output_profile},
        )

    status = "degraded" if fallbacks or errors else "ok"

    if request.require_crosscheck:
        primary_spec = next(s for s in routes if s.source_id == primary_source)
        crosschecked = False
        for source in routes:
            if source.source_id == primary_source or source.independence_group == primary_spec.independence_group:
                continue
            adapter = adapters.get(source.source_id)
            if adapter is None or not getattr(adapter, "supports", lambda *_: False)(request, instrument):
                continue
            crosschecked = True
            try:
                secondary = adapter.fetch(request, instrument)
                if not secondary:
                    raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, f"{source.source_id} returned empty cross-check data")
                validation_errors = _validate_points(secondary)
                if validation_errors:
                    raise FinancialDataError(
                        ErrorCode.VALIDATION_FAILED,
                        f"{source.source_id} cross-check failed validation",
                        {"issues": validation_errors},
                    )
                health_tracker.record_success(source.source_id)
                sources_used.append(source.source_id)
                conflicts: list[dict[str, Any]] = []
                for a, b in _find_comparable(primary_points, secondary):
                    flags = compare_points(a, b)
                    if flags:
                        for flag in flags:
                            if flag not in a.quality_flags:
                                a.quality_flags.append(flag)
                        conflicts.append({
                            "field": a.field,
                            "primary_source": a.source_id,
                            "primary_value": a.value,
                            "secondary_source": b.source_id,
                            "secondary_value": b.value,
                            "flags": flags,
                        })
                if conflicts:
                    errors.append(
                        FinancialDataError(
                            ErrorCode.SOURCE_CONFLICT,
                            "Independent sources disagree beyond validation tolerance",
                            {"conflicts": conflicts},
                        )
                    )
                    status = "conflict"
                break
            except FinancialDataError as exc:
                errors.append(exc)
                health_tracker.record_failure(source.source_id, exc.message)
                status = "degraded"
                break
        if not crosschecked:
            errors.append(
                FinancialDataError(
                    ErrorCode.SOURCE_UNAVAILABLE,
                    "Cross-check was required but no independent executable source is available",
                    {"primary_source": primary_source},
                )
            )
            status = "degraded"

    return DataResult(
        data=primary_points,
        errors=errors,
        sources_used=sources_used,
        fallbacks_used=fallbacks,
        status=status,
        metadata={
            "instrument": instrument.ticker,
            "canonical_id": instrument.canonical_id,
            "output_profile": request.output_profile,
            "field": request.field,
        },
    )


def result_dict(result: DataResult, profile: Optional[str] = None) -> dict[str, Any]:
    profile = profile or str(result.metadata.get("output_profile", "standard"))
    return compress_result(result, profile)


def _merge_results(results: Iterable[DataResult], *, workflow: str) -> DataResult:
    data: list[DataPoint] = []
    errors: list[FinancialDataError] = []
    sources: list[str] = []
    fallbacks: list[dict[str, str]] = []
    statuses: list[str] = []
    for result in results:
        data.extend(result.data)
        errors.extend(result.errors)
        for source in result.sources_used:
            if source not in sources:
                sources.append(source)
        fallbacks.extend(result.fallbacks_used)
        statuses.append(result.status)
    if "conflict" in statuses:
        status = "conflict"
    elif all(s == "failed" for s in statuses) if statuses else True:
        status = "failed"
    elif any(s in {"failed", "degraded"} for s in statuses):
        status = "degraded"
    else:
        status = "ok"
    return DataResult(data=data, errors=errors, sources_used=sources, fallbacks_used=fallbacks, status=status, metadata={"workflow": workflow})


def single_stock_snapshot(symbol: str, *, adapters: Optional[dict[str, Any]] = None) -> DataResult:
    try:
        inst = InstrumentMaster().resolve(symbol)
    except FinancialDataError as exc:
        return DataResult(errors=[exc], status="failed", metadata={"workflow": "single_stock_snapshot"})
    if inst.country == "CN":
        return get_data(DataRequest(symbol, "quote"), adapters=adapters)
    if inst.country == "US":
        return get_data(DataRequest(symbol, "fundamentals"), adapters=adapters)
    return DataResult(
        errors=[FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"single_stock_snapshot v0.1.0 does not yet support {inst.country}")],
        status="failed",
        metadata={"workflow": "single_stock_snapshot"},
    )


def peer_comparison(symbols: Iterable[str], fields: Iterable[str], *, adapters: Optional[dict[str, Any]] = None) -> DataResult:
    results: list[DataResult] = []
    for symbol in symbols:
        for field in fields:
            results.append(get_data(DataRequest(symbol, field), adapters=adapters))
    return _merge_results(results, workflow="peer_comparison")


def macro_snapshot(*, adapters: Optional[dict[str, Any]] = None) -> DataResult:
    result = get_data(DataRequest("USTCURVE", "yield_curve", market="US"), adapters=adapters)
    result.metadata["workflow"] = "macro_snapshot"
    return result


def event_dataset(symbol: str, *, form: Optional[str] = None, adapters: Optional[dict[str, Any]] = None) -> DataResult:
    params = {"form": form} if form else {}
    result = get_data(DataRequest(symbol, "filings", params=params), adapters=adapters)
    result.metadata["workflow"] = "event_dataset"
    return result


def market_breadth_snapshot(changes: Iterable[float]) -> dict[str, Union[float, int]]:
    return market_breadth(changes)


def sector_rotation_dataset(*args: Any, **kwargs: Any) -> DataResult:
    return DataResult(
        errors=[FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, "sector_rotation_dataset requires a sector-classification/market-wide adapter planned for a later minor version")],
        status="failed",
        metadata={"workflow": "sector_rotation_dataset"},
    )


def cross_section_fundamentals(field: str, *, period: str) -> DataResult:
    return DataResult(
        errors=[FinancialDataError(
            ErrorCode.FIELD_NOT_SUPPORTED,
            "cross_section_fundamentals requires the SEC Frames adapter planned for a later minor version",
            {"field": field, "period": period},
        )],
        status="failed",
        metadata={"workflow": "cross_section_fundamentals"},
    )
