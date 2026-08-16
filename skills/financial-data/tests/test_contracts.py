from datetime import datetime, timezone
import pytest

from financial_data.contracts import (
    DataPoint,
    DataRequest,
    DataResult,
    ErrorCode,
    FinancialDataError,
    QualityFlag,
)


def test_datapoint_requires_provenance_and_serializes():
    point = DataPoint(
        instrument_id="equity_cn_600519",
        symbol="600519.SH",
        field="turnover",
        value=6_830_000_000,
        unit="CNY",
        currency="CNY",
        as_of="2026-08-14T15:00:00+08:00",
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        source_id="tencent",
        source_type="secondary",
        status="verified",
    )
    payload = point.to_dict()
    assert payload["source_id"] == "tencent"
    assert payload["quality_flags"] == []
    assert point.quality_flags == []


def test_request_defaults_are_stable():
    req = DataRequest(instrument="AAPL", field="filings")
    assert req.output_profile == "standard"
    assert req.require_crosscheck is False
    assert req.debug is False


def test_error_code_and_payload_are_stable():
    err = FinancialDataError(ErrorCode.SOURCE_CONFLICT, "values disagree", {"a": 1, "b": 2})
    assert err.code.value == "SOURCE_CONFLICT"
    assert err.to_dict()["details"]["a"] == 1


def test_datapoint_rejects_missing_provenance():
    with pytest.raises(ValueError, match="source_id"):
        DataPoint(
            instrument_id="equity_us_AAPL",
            symbol="AAPL.US",
            field="price",
            value=1,
            unit="USD",
            currency="USD",
            as_of="2026-08-14T20:00:00+00:00",
            retrieved_at="2026-08-14T20:00:01+00:00",
            source_id="",
            source_type="secondary",
        )


def test_result_serializes_nested_errors_and_points():
    result = DataResult(
        data=[],
        errors=[FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "down")],
        status="failed",
    )
    assert result.to_dict()["errors"][0]["code"] == "SOURCE_UNAVAILABLE"
