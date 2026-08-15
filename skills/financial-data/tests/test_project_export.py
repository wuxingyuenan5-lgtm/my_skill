import pytest
from financial_data.project_export import build_project_manifest, render_manifest_markdown
INDEX={"capabilities":[{"id":"cn_equity_quote","status":"READY","primary_sources":["tencent"],"fallback_sources":["sina"],"auth":"none","reference":"a-share-market-data.md","runtime":"financial_data.adapters.tencent:TencentAdapter","last_verified":"2026-08-15"},{"id":"tradingview_advanced_own_data","status":"RESTRICTED","primary_sources":["project_datafeed"],"fallback_sources":[],"auth":"tradingview_library_access","reference":"tradingview.md","last_verified":"2026-08-15"}]}

def test_build_project_manifest_collects_selected_capabilities_and_sources():
    out=build_project_manifest(INDEX,["cn_equity_quote","tradingview_advanced_own_data"],project_name="dashboard")
    assert out["primary_sources"]==["tencent","project_datafeed"]; assert out["fallback_sources"]==["sina"]; assert out["restricted_capabilities"]==["tradingview_advanced_own_data"]

def test_missing_capability_id_is_explicit_error():
    with pytest.raises(KeyError): build_project_manifest(INDEX,["does_not_exist"])

def test_render_manifest_markdown_is_copyable_summary():
    text=render_manifest_markdown(build_project_manifest(INDEX,["cn_equity_quote"],project_name="demo")); assert "# demo data pack" in text; assert "tencent" in text
