from financial_data.cftc import build_cot_query, parse_cot_rows


def test_build_cot_query_is_bounded_and_filters_market_safely():
    q = build_cot_query(limit=25, market_contains="GOLD")
    assert q["$limit"] == 25
    assert "GOLD" in q["$where"]
    assert q["$order"].endswith("DESC")


def test_parse_cot_rows_keeps_raw_fields_and_normalized_date():
    rows = [{"report_date_as_yyyy_mm_dd":"2026-08-11T00:00:00.000","contract_market_name":"GOLD - COMMODITY EXCHANGE INC.","cftc_contract_market_code":"088691","open_interest_all":"500000","noncomm_positions_long_all":"250000"}]
    out = parse_cot_rows(rows)
    assert out[0]["report_date"] == "2026-08-11"
    assert out[0]["market"] == "GOLD - COMMODITY EXCHANGE INC."
    assert out[0]["cftc_contract_code"] == "088691"
    assert out[0]["open_interest"] == 500000
    assert out[0]["raw"]["noncomm_positions_long_all"] == "250000"
