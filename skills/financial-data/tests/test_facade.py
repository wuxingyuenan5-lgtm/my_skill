from financial_data.contracts import DataPoint, DataRequest, ErrorCode, FinancialDataError, QualityFlag
from financial_data.facade import (
    cross_section_fundamentals,
    get_data,
    macro_snapshot,
    market_breadth_snapshot,
)
from financial_data.instruments import InstrumentMaster
from financial_data.registry import default_registry


class FailAdapter:
    source_id = "tencent"
    def supports(self, request, instrument):
        return True
    def fetch(self, request, instrument):
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "primary down")


class QuoteAdapter:
    def __init__(self, source_id, value):
        self.source_id = source_id
        self.value = value
    def supports(self, request, instrument):
        return request.field in {"quote", "price"}
    def fetch(self, request, instrument):
        return [DataPoint(
            instrument_id=instrument.canonical_id,
            symbol=instrument.ticker,
            field="price",
            value=self.value,
            unit="CNY",
            currency="CNY",
            trade_date="2026-08-14",
            as_of="2026-08-14T15:00:00+08:00",
            retrieved_at="2026-08-14T15:00:01+08:00",
            source_id=self.source_id,
            source_type="secondary",
            status="verified",
        )]


class TreasuryFake:
    source_id = "treasury"
    def supports(self, request, instrument):
        return request.field == "yield_curve"
    def fetch(self, request, instrument):
        common = dict(
            instrument_id=instrument.canonical_id, symbol=instrument.ticker, unit="ratio", currency=None,
            trade_date="2026-08-14", as_of="2026-08-14T00:00:00+00:00",
            retrieved_at="2026-08-15T00:00:00+00:00", source_id="treasury", status="verified"
        )
        return [
            DataPoint(field="yield_2y", value=0.042, source_type="primary", **common),
            DataPoint(field="yield_10y", value=0.0455, source_type="primary", **common),
            DataPoint(field="spread_10y_2y", value=0.0035, source_type="derived", **common),
        ]


def test_primary_failure_falls_back_to_independent_source():
    result = get_data(
        DataRequest("600519", "quote"),
        adapters={"tencent": FailAdapter(), "sina": QuoteAdapter("sina", 100.0)},
    )
    assert result.status == "degraded"
    assert result.data[0].source_id == "sina"
    assert QualityFlag.FALLBACK_USED.value in result.data[0].quality_flags
    assert result.fallbacks_used == [{"from": "tencent", "to": "sina"}]
    assert result.errors[0].code == ErrorCode.SOURCE_UNAVAILABLE


def test_crosscheck_surfaces_source_conflict_without_hiding_primary_value():
    result = get_data(
        DataRequest("600519", "quote", require_crosscheck=True),
        adapters={"tencent": QuoteAdapter("tencent", 100.0), "sina": QuoteAdapter("sina", 103.0)},
    )
    assert result.status == "conflict"
    assert result.data[0].value == 100.0
    assert QualityFlag.SOURCE_CONFLICT.value in result.data[0].quality_flags
    assert any(e.code == ErrorCode.SOURCE_CONFLICT for e in result.errors)
    assert result.sources_used == ["tencent", "sina"]


def test_commercial_request_with_only_restricted_quote_sources_returns_compliance_error():
    result = get_data(DataRequest("600519", "quote", params={"usage": "commercial"}), adapters={})
    assert result.status == "failed"
    assert result.errors[0].code == ErrorCode.COMPLIANCE_RESTRICTED


def test_unsupported_field_is_explicit_not_empty_success():
    result = get_data(DataRequest("600519", "imaginary_field"), adapters={})
    assert result.status == "failed"
    assert result.errors[0].code == ErrorCode.FIELD_NOT_SUPPORTED


def test_macro_snapshot_composes_data_not_investment_view():
    result = macro_snapshot(adapters={"treasury": TreasuryFake()})
    assert result.status == "ok"
    assert {p.field for p in result.data} == {"yield_2y", "yield_10y", "spread_10y_2y"}
    assert "recommendation" not in result.metadata


def test_market_breadth_snapshot_is_local_and_reproducible():
    assert market_breadth_snapshot([0.1, -0.2, 0.0, 0.03])["advancers"] == 2


def test_unimplemented_cross_section_is_explicit():
    result = cross_section_fundamentals("revenue", period="CY2026Q2")
    assert result.status == "failed"
    assert result.errors[0].code == ErrorCode.FIELD_NOT_SUPPORTED
