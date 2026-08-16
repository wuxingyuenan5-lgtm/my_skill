import pytest

from financial_data.contracts import DataRequest, ErrorCode, FinancialDataError
from financial_data.instruments import Instrument
from financial_data.adapters.tencent import TencentAdapter, parse_tencent_kline_payload
from financial_data.adapters.yahoo_chart import YahooChartAdapter, parse_yahoo_chart_payload


CN = Instrument("equity_cn_600519_SH", "600519", "SSE", "600519.SH", None, "equity", "CNY", "CN")
US = Instrument("equity_us_AAPL_US", "AAPL", "NASDAQ", "AAPL.US", None, "equity", "USD", "US")
HK = Instrument("equity_hk_0700_HK", "0700", "HKEX", "0700.HK", None, "equity", "HKD", "HK")


def test_tencent_daily_kline_parser_returns_bar_points():
    payload = {"code": 0, "data": {"sh600519": {"qfqday": [["2026-08-13", "1400", "1410", "1420", "1395", "12345", "99"]]}}}
    out = parse_tencent_kline_payload(payload, CN, resolution="1d", retrieved_at="2026-08-15T05:00:00+00:00", adjustment="qfq")
    assert out[0].field == "bar"
    assert out[0].value["open"] == 1400.0 and out[0].value["close"] == 1410.0
    assert out[0].trade_date == "2026-08-13"
    assert out[0].adjustment == "qfq"


def test_tencent_minute_kline_preserves_unknown_extra_field():
    payload = {"code": 0, "data": {"sh600519": {"m5": [["202608151005", "1400", "1402", "1405", "1399", "321", "7.5"]]}}}
    out = parse_tencent_kline_payload(payload, CN, resolution="5m", retrieved_at="2026-08-15T05:00:00+00:00", adjustment="none")
    assert out[0].value["volume"] == 321.0
    assert out[0].metadata["provider_extra_fields"] == ["7.5"]
    assert out[0].as_of.endswith("+08:00")


def test_tencent_adapter_rejects_unknown_kline_resolution():
    adapter = TencentAdapter(session=None)
    with pytest.raises(FinancialDataError) as exc:
        adapter._kline_request(DataRequest("600519.SH", "kline", params={"resolution": "2h"}), CN)
    assert exc.value.code == ErrorCode.FIELD_NOT_SUPPORTED


def test_yahoo_chart_parser_skips_null_ohlc_rows_and_keeps_exchange_timezone():
    payload = {
        "chart": {
            "error": None,
            "result": [{
                "meta": {"currency": "USD", "exchangeTimezoneName": "America/New_York"},
                "timestamp": [1786541400, 1786627800],
                "indicators": {
                    "quote": [{"open": [100, None], "high": [102, None], "low": [99, None], "close": [101, None], "volume": [1000, None]}],
                    "adjclose": [{"adjclose": [100.5, None]}],
                },
            }],
        }
    }
    out = parse_yahoo_chart_payload(payload, US, retrieved_at="2026-08-15T05:00:00+00:00", interval="1d")
    assert len(out) == 1
    assert out[0].value["close"] == 101.0
    assert out[0].metadata["exchange_timezone"] == "America/New_York"
    assert out[0].value["adj_close"] == 100.5


def test_yahoo_chart_parser_surfaces_provider_error():
    payload = {"chart": {"result": None, "error": {"code": "Not Found", "description": "No data"}}}
    with pytest.raises(FinancialDataError) as exc:
        parse_yahoo_chart_payload(payload, US, retrieved_at="x", interval="1d")
    assert exc.value.code == ErrorCode.SOURCE_UNAVAILABLE


def test_yahoo_symbol_mapping_for_us_and_hk():
    assert YahooChartAdapter.provider_symbol(US) == "AAPL"
    assert YahooChartAdapter.provider_symbol(HK) == "0700.HK"


def test_yahoo_non_equity_symbol_mapping_and_unit(monkeypatch):
    """2026-08-16 实测：指数 / 商品期货 / 外汇 / 美元指数期货 / 国债收益率指数。
    ^ 前缀与 =F / =X 后缀 / DX-Y.NYB 原生记号直通；^TNX 等收益率指数打 unit=% 标记。"""
    from financial_data.adapters.yahoo_chart import _yield_unit

    def mk(symbol, country="US"):
        return Instrument(f"x_{symbol}", symbol, "E", symbol, None, "index", "USD", country)

    assert YahooChartAdapter.provider_symbol(mk("^GSPC")) == "^GSPC"
    assert YahooChartAdapter.provider_symbol(mk("^TNX")) == "^TNX"
    assert YahooChartAdapter.provider_symbol(mk("GC=F")) == "GC=F"
    assert YahooChartAdapter.provider_symbol(mk("CNY=X")) == "CNY=X"
    assert YahooChartAdapter.provider_symbol(mk("DX-Y.NYB")) == "DX-Y.NYB"

    assert _yield_unit("^TNX") == "%"
    assert _yield_unit("^TYX") == "%"
    assert _yield_unit("^GSPC") is None
    assert _yield_unit("GC=F") is None

    # 非 US/HK country + 非原生记号 → 不支持（如 CN 股票）
    cn_equity = Instrument("equity_cn_600519_SH", "600519", "SSE", "600519.SH", None, "equity", "CNY", "CN")
    adapter = YahooChartAdapter()
    assert adapter.supports(DataRequest("600519.SH", "kline", params={}), cn_equity) is False
    # 指数 symbol 即使 country 非 US/HK 也放行（Yahoo 原生记号）
    assert adapter.supports(DataRequest("^GSPC", "kline", params={}), mk("^GSPC")) is True
