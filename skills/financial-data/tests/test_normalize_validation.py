from datetime import datetime
import pytest

from financial_data.contracts import DataPoint, DataResult, QualityFlag
from financial_data.normalize import (
    normalize_number,
    normalize_percentage,
    normalize_timestamp,
)
from financial_data.validation import (
    compare_points,
    compare_values,
    compress_result,
    validate_ohlcv,
    validate_timeseries,
)


def _point(value, source="a", unit="CNY", currency="CNY"):
    return DataPoint(
        instrument_id="equity_cn_600519_SH",
        symbol="600519.SH",
        field="turnover",
        value=value,
        unit=unit,
        currency=currency,
        as_of="2026-08-14T15:00:00+08:00",
        retrieved_at="2026-08-14T15:00:01+08:00",
        source_id=source,
        source_type="secondary",
        status="verified",
    )


def test_percent_normalizes_to_decimal():
    assert normalize_percentage("3.21%") == pytest.approx(0.0321)
    assert normalize_percentage(3.21, percent_points=True) == pytest.approx(0.0321)
    assert normalize_percentage(0.0321) == pytest.approx(0.0321)


def test_number_supports_explicit_financial_suffixes():
    assert normalize_number("1.25亿") == 125_000_000
    assert normalize_number("3,500万") == 35_000_000
    assert normalize_number("1.2B") == 1_200_000_000


def test_timestamp_rejects_naive_without_timezone():
    with pytest.raises(ValueError, match="timezone"):
        normalize_timestamp("2026-08-14T15:00:00")
    assert normalize_timestamp("2026-08-14T15:00:00", default_timezone="Asia/Shanghai").endswith("+08:00")


def test_ohlcv_rejects_invalid_high_and_negative_volume():
    errors = validate_ohlcv({"open": 10, "high": 9, "low": 8, "close": 9.5, "volume": -1})
    assert any("high" in e.lower() for e in errors)
    assert any("volume" in e.lower() for e in errors)


def test_timeseries_rejects_duplicate_or_unsorted_timestamps():
    rows = [{"date": "2026-08-14"}, {"date": "2026-08-13"}, {"date": "2026-08-13"}]
    errors = validate_timeseries(rows, time_key="date")
    assert any("sorted" in e.lower() for e in errors)
    assert any("duplicate" in e.lower() for e in errors)


def test_cross_source_conflict_is_explicit():
    assert compare_values(100.0, 103.0, rel_tol=0.005) is False
    flags = compare_points(_point(100.0, "a"), _point(103.0, "b"), rel_tol=0.005)
    assert QualityFlag.SOURCE_CONFLICT.value in flags


def test_unit_or_currency_mismatch_conflicts_before_numeric_compare():
    flags = compare_points(_point(100.0, "a", unit="CNY"), _point(100.0, "b", unit="USD", currency="USD"))
    assert QualityFlag.UNIT_MISMATCH.value in flags
    assert QualityFlag.CURRENCY_MISMATCH.value in flags


def test_compact_output_preserves_provenance_but_drops_diagnostics():
    result = DataResult(data=[_point(100.0)], sources_used=["a"], status="ok", metadata={"raw": {"huge": True}, "request_id": "x"})
    compact = compress_result(result, "compact")
    assert compact["data"][0]["source_id"] == "a"
    assert "raw" not in compact["metadata"]
    assert compact["metadata"]["request_id"] == "x"
