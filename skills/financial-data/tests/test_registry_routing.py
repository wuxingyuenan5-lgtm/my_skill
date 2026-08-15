from financial_data.contracts import DataRequest
from financial_data.instruments import InstrumentMaster
from financial_data.registry import SourceHealthTracker, default_registry
from financial_data.routing import Router


def test_sec_wins_for_us_filings():
    inst = InstrumentMaster().resolve("AAPL")
    routes = Router(default_registry()).route(DataRequest("AAPL", "filings"), inst)
    assert routes[0].source_id == "sec_edgar"


def test_cn_quote_prefers_tencent_and_has_independent_fallback():
    inst = InstrumentMaster().resolve("600519")
    routes = Router(default_registry()).route(DataRequest("600519", "quote"), inst)
    assert routes[0].source_id == "tencent"
    assert routes[1].source_id == "sina"
    assert routes[0].independence_group != routes[1].independence_group


def test_cn_kline_prefers_tencent():
    inst = InstrumentMaster().resolve("600519")
    routes = Router(default_registry()).route(DataRequest("600519", "kline"), inst)
    assert routes[0].source_id == "tencent"


def test_us_and_hk_kline_prefer_yahoo_chart():
    us = InstrumentMaster().resolve("AAPL")
    hk = InstrumentMaster().resolve("0700.HK")
    assert Router(default_registry()).route(DataRequest("AAPL", "kline"), us)[0].source_id == "yahoo"
    assert Router(default_registry()).route(DataRequest("0700.HK", "kline"), hk)[0].source_id == "yahoo"


def test_us_yield_curve_is_treasury_official():
    inst = InstrumentMaster().resolve("UST10Y", market="US")
    routes = Router(default_registry()).route(DataRequest("UST10Y", "yield_curve", market="US"), inst)
    assert routes[0].source_id == "treasury"
    assert routes[0].authority == "A"


def test_broken_source_is_removed_from_routes():
    tracker = SourceHealthTracker()
    tracker.record_failure("tencent", "timeout")
    tracker.record_failure("tencent", "timeout")
    tracker.record_failure("tencent", "timeout")
    inst = InstrumentMaster().resolve("600519")
    routes = Router(default_registry(), health_tracker=tracker).route(DataRequest("600519", "quote"), inst)
    assert routes[0].source_id == "sina"


def test_degraded_source_remains_but_is_penalized():
    tracker = SourceHealthTracker()
    tracker.record_failure("tencent", "timeout")
    inst = InstrumentMaster().resolve("600519")
    routes = Router(default_registry(), health_tracker=tracker).route(DataRequest("600519", "quote"), inst)
    assert {r.source_id for r in routes[:2]} == {"tencent", "sina"}


def test_commercial_usage_filters_research_only_source():
    inst = InstrumentMaster().resolve("600519")
    routes = Router(default_registry()).route(
        DataRequest("600519", "quote", params={"usage": "commercial"}), inst
    )
    assert all(r.commercial_use == "allowed" for r in routes)


def test_registry_marks_yahoo_chart_as_executable_but_cboe_as_recipe_only():
    registry = default_registry()
    assert registry.get("yahoo").adapter == "yahoo_chart"
    cboe = registry.get("cboe")
    assert cboe.adapter is None
    assert cboe.compliance == "C"
