from __future__ import annotations

from math import isclose
from typing import Any

from .contracts import DataPoint, DataResult, QualityFlag


def validate_ohlcv(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ("open", "high", "low", "close")
    missing = [k for k in required if row.get(k) is None]
    if missing:
        errors.append(f"VALIDATION_FAILED: missing OHLC fields: {', '.join(missing)}")
        return errors
    o, h, l, c = (float(row[k]) for k in required)
    if h < max(o, l, c):
        errors.append("VALIDATION_FAILED: high is below open/low/close")
    if l > min(o, h, c):
        errors.append("VALIDATION_FAILED: low is above open/high/close")
    for key in ("volume", "turnover", "amount"):
        if row.get(key) is not None and float(row[key]) < 0:
            errors.append(f"VALIDATION_FAILED: {key} cannot be negative")
    return errors


def validate_timeseries(rows: list[dict[str, Any]], *, time_key: str = "date") -> list[str]:
    errors: list[str] = []
    times = [row.get(time_key) for row in rows]
    if any(t is None for t in times):
        errors.append(f"VALIDATION_FAILED: missing {time_key}")
        return errors
    if times != sorted(times):
        errors.append(f"VALIDATION_FAILED: {time_key} is not sorted ascending")
    if len(set(times)) != len(times):
        errors.append(f"VALIDATION_FAILED: duplicate {time_key} values")
    return errors


def validate_point(point: DataPoint) -> list[str]:
    errors: list[str] = []
    if point.value is None:
        errors.append("VALIDATION_FAILED: value is missing")
    if point.field in {"volume", "turnover", "market_cap", "float_market_cap"}:
        try:
            if float(point.value) < 0:
                errors.append(f"VALIDATION_FAILED: {point.field} cannot be negative")
        except (TypeError, ValueError):
            errors.append(f"VALIDATION_FAILED: {point.field} must be numeric")
    return errors


def compare_values(a: Any, b: Any, *, rel_tol: float = 0.005, abs_tol: float = 0.0) -> bool:
    try:
        return isclose(float(a), float(b), rel_tol=rel_tol, abs_tol=abs_tol)
    except (TypeError, ValueError):
        return a == b


def compare_points(a: DataPoint, b: DataPoint, *, rel_tol: float = 0.005, abs_tol: float = 0.0) -> list[str]:
    flags: list[str] = []
    if a.unit != b.unit:
        flags.append(QualityFlag.UNIT_MISMATCH.value)
    if a.currency != b.currency:
        flags.append(QualityFlag.CURRENCY_MISMATCH.value)
    if flags:
        return flags
    if a.field != b.field or a.instrument_id != b.instrument_id:
        return [QualityFlag.SOURCE_CONFLICT.value]
    if not compare_values(a.value, b.value, rel_tol=rel_tol, abs_tol=abs_tol):
        flags.append(QualityFlag.SOURCE_CONFLICT.value)
    return flags


def compress_result(result: DataResult, profile: str = "standard") -> dict[str, Any]:
    payload = result.to_dict()
    if profile == "full":
        return payload
    metadata = {k: v for k, v in payload["metadata"].items() if k not in {"raw", "provider_raw", "debug"}}
    payload["metadata"] = metadata
    if profile == "compact":
        # Compact still preserves full provenance fields; it trims extended metadata only.
        for point in payload["data"]:
            point["metadata"] = {
                k: v for k, v in point.get("metadata", {}).items()
                if k in {"taxonomy_tag", "provider_field", "form", "filed", "source_url"}
            }
            point.pop("parameters", None)
            if not point.get("derived_from"):
                point.pop("derived_from", None)
            if point.get("algorithm_version") is None:
                point.pop("algorithm_version", None)
    return payload
