import json
from pathlib import Path
import pytest

from financial_data.contracts import DataRequest, ErrorCode, FinancialDataError, QualityFlag
from financial_data.instruments import InstrumentMaster
from financial_data.adapters.base import HttpClient
from financial_data.adapters.tencent import TencentAdapter, parse_tencent_quote_text
from financial_data.adapters.sina import SinaAdapter, parse_sina_quote_text
from financial_data.adapters.sec_edgar import SecEdgarAdapter
from financial_data.adapters.treasury import TreasuryAdapter

FIX = Path(__file__).parent / "fixtures"


class FakeResponse:
    def __init__(self, *, text="", payload=None, status_code=200, content=None):
        self.text = text
        self._payload = payload
        self.status_code = status_code
        self.content = content if content is not None else text.encode("utf-8")
        self.headers = {}

    def json(self):
        if self._payload is None:
            return json.loads(self.text)
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if not self.responses:
            raise AssertionError("unexpected HTTP call")
        return self.responses.pop(0)


def test_http_client_maps_rate_limit_after_finite_retry():
    session = FakeSession([FakeResponse(status_code=429), FakeResponse(status_code=429), FakeResponse(status_code=429)])
    client = HttpClient(session=session, sleeper=lambda _: None, max_retries=2)
    with pytest.raises(FinancialDataError) as exc:
        client.get_text("https://example.com")
    assert exc.value.code == ErrorCode.RATE_LIMITED
    assert len(session.calls) == 3


def test_tencent_parser_normalizes_provider_units_and_percentages():
    text = (FIX / "tencent_quote.txt").read_text(encoding="utf-8")
    inst = InstrumentMaster().resolve("600519")
    points = parse_tencent_quote_text(text, inst, retrieved_at="2026-08-14T15:00:01+08:00")
    by_field = {p.field: p for p in points}
    assert by_field["price"].value == 1500.0
    assert by_field["turnover"].value == pytest.approx(3_456_789_000)
    assert by_field["turnover_rate"].value == pytest.approx(0.0056)
    assert by_field["market_cap"].value == pytest.approx(1.9e12)
    assert by_field["pe_ttm"].value == 22.5
    assert by_field["price"].trade_date == "2026-08-14"


def test_sina_parser_is_independent_quote_fallback():
    text = (FIX / "sina_quote.txt").read_text(encoding="utf-8")
    inst = InstrumentMaster().resolve("600519")
    points = parse_sina_quote_text(text, inst, retrieved_at="2026-08-14T15:00:01+08:00")
    by_field = {p.field: p for p in points}
    assert by_field["price"].value == 1500.0
    assert by_field["volume"].unit == "shares"
    assert by_field["turnover"].value == 3_456_789_000.0
    assert by_field["price"].source_id == "sina"


def test_sec_adapter_maps_ticker_to_cik_and_extracts_latest_metrics(monkeypatch):
    tickers = json.loads((FIX / "sec_tickers.json").read_text())
    facts = json.loads((FIX / "sec_companyfacts.json").read_text())
    session = FakeSession([FakeResponse(payload=tickers), FakeResponse(payload=facts)])
    monkeypatch.setenv("SEC_CONTACT", "Research User research@example.com")
    adapter = SecEdgarAdapter(session=session, clock=lambda: "2026-08-15T00:00:00+00:00")
    inst = InstrumentMaster().resolve("AAPL")
    req = DataRequest("AAPL", "fundamentals", params={"metrics": ["revenue", "net_income", "operating_cash_flow"]})
    points = adapter.fetch(req, inst)
    by_field = {p.field: p for p in points}
    assert by_field["revenue"].value == 94_000_000_000
    assert by_field["revenue"].report_period == "2026-06-27"
    assert by_field["revenue"].metadata["taxonomy_tag"] == "RevenueFromContractWithCustomerExcludingAssessedTax"
    assert by_field["net_income"].source_type == "primary"


def test_sec_adapter_requires_declared_contact(monkeypatch):
    monkeypatch.delenv("SEC_CONTACT", raising=False)
    adapter = SecEdgarAdapter(session=FakeSession([]))
    inst = InstrumentMaster().resolve("AAPL")
    with pytest.raises(FinancialDataError) as exc:
        adapter.fetch(DataRequest("AAPL", "filings"), inst)
    assert exc.value.code == ErrorCode.AUTH_REQUIRED


def test_sec_filings_preserve_publish_date_and_document_url(monkeypatch):
    tickers = json.loads((FIX / "sec_tickers.json").read_text())
    submissions = json.loads((FIX / "sec_submissions.json").read_text())
    session = FakeSession([FakeResponse(payload=tickers), FakeResponse(payload=submissions)])
    monkeypatch.setenv("SEC_CONTACT", "Research User research@example.com")
    adapter = SecEdgarAdapter(session=session, clock=lambda: "2026-08-15T00:00:00+00:00")
    points = adapter.fetch(DataRequest("AAPL", "filings", params={"form": "10-Q"}), InstrumentMaster().resolve("AAPL"))
    assert len(points) == 1
    assert points[0].publish_date == "2026-07-31"
    assert "Archives/edgar/data/320193/" in points[0].value["url"]


def test_treasury_adapter_normalizes_yields_to_decimal_and_derives_spread():
    csv_text = (FIX / "treasury_yield.csv").read_text()
    session = FakeSession([FakeResponse(text=csv_text)])
    adapter = TreasuryAdapter(session=session, clock=lambda: "2026-08-15T00:00:00+00:00")
    inst = InstrumentMaster().resolve("UST10Y", market="US")
    points = adapter.fetch(DataRequest("UST10Y", "yield_curve", market="US"), inst)
    by_field = {p.field: p for p in points}
    assert by_field["yield_2y"].value == pytest.approx(0.042)
    assert by_field["yield_10y"].value == pytest.approx(0.0455)
    assert by_field["spread_10y_2y"].value == pytest.approx(0.0035)
    assert by_field["spread_10y_2y"].source_type == "derived"
    assert by_field["yield_10y"].trade_date == "2026-08-14"
