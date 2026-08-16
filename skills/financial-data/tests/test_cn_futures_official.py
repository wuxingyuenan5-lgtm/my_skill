import io
import zipfile

import pytest

from financial_data.cn_futures_official import (
    fetch_cn_futures_daily,
    normalize_trade_date,
    parse_cffex_daily_csv,
    parse_cffex_history_zip,
    parse_czce_daily_text,
    parse_dce_daily_payload,
    parse_gfex_daily_payload,
    parse_ine_daily_payload,
    parse_shfe_daily_payload,
    validate_futures_daily_row,
)
from financial_data.contracts import ErrorCode, FinancialDataError
from financial_data.futures import select_dominant_contract, term_structure


def test_normalize_and_validation_basics():
    assert normalize_trade_date("20260814") == "2026-08-14"
    bad = {
        "contract_id": "CU2609",
        "trade_date": "2026-08-14",
        "open": 100,
        "high": 99,
        "low": 98,
        "close": 100,
        "volume": -1,
        "open_interest": 2,
        "turnover": 3,
    }
    errors = validate_futures_daily_row(bad)
    assert any("high" in item for item in errors)
    assert any("volume" in item for item in errors)


def test_shfe_structured_payload_filters_summary_and_keeps_settlement():
    payload = {
        "o_curinstrument": [
            {
                "PRODUCTGROUPID": "cu",
                "DELIVERYMONTH": "2609",
                "OPENPRICE": "80000",
                "HIGHESTPRICE": "81000",
                "LOWESTPRICE": "79000",
                "CLOSEPRICE": "80500",
                "SETTLEMENTPRICE": "80300",
                "PRESETTLEMENTPRICE": "79800",
                "VOLUME": "123",
                "OPENINTEREST": "789",
                "TURNOVER": "456.7",
            },
            {"PRODUCTGROUPID": "cu", "DELIVERYMONTH": "小计"},
        ]
    }
    rows = parse_shfe_daily_payload(payload, "20260814", "u")
    assert len(rows) == 1
    assert rows[0]["contract_id"] == "CU2609"
    assert rows[0]["delivery_month"] == "2609"
    assert rows[0]["settlement"] == 80300
    assert rows[0]["pre_settlement"] == 79800
    assert rows[0]["close"] == 80500


def test_ine_productid_fallback():
    payload = {
        "o_curinstrument": [
            {
                "PRODUCTID": "sc_f",
                "DELIVERYMONTH": "2609",
                "OPENPRICE": 500,
                "HIGHESTPRICE": 510,
                "LOWESTPRICE": 490,
                "CLOSEPRICE": 505,
                "SETTLEMENTPRICE": 503,
                "PRESETTLEMENTPRICE": 498,
                "VOLUME": 3,
                "OPENINTEREST": 4,
                "TURNOVER": 5,
            }
        ]
    }
    row = parse_ine_daily_payload(payload, "20260814", "u")[0]
    assert row["contract_id"] == "SC2609"
    assert row["delivery_month"] == "2609"


def test_structured_payload_failure_is_explicit():
    with pytest.raises(FinancialDataError):
        parse_shfe_daily_payload({"data": []}, "20260814", "u")


def test_dce_and_gfex_json_rows():
    dce = {
        "data": [
            {
                "variety": "豆粕",
                "contractId": "m2609",
                "open": "3000",
                "high": "3100",
                "low": "2950",
                "close": "3050",
                "lastClear": "2990",
                "clearPrice": "3040",
                "volumn": "100",
                "openInterest": "200",
                "turnover": "999",
            }
        ]
    }
    dce_row = parse_dce_daily_payload(dce, "20260814", "u")[0]
    assert dce_row["contract_id"] == "M2609"
    assert dce_row["delivery_month"] == "2609"

    gfex = {
        "data": [
            {
                "variety": "碳酸锂",
                "varietyOrder": "lc",
                "delivMonth": "2609",
                "open": "80000",
                "high": "81000",
                "low": "79000",
                "close": "80500",
                "lastClear": "79800",
                "clearPrice": "80300",
                "volumn": "100",
                "openInterest": "200",
                "turnover": "999",
            }
        ]
    }
    row = parse_gfex_daily_payload(gfex, "20260814", "u")[0]
    assert row["contract_id"] == "LC2609"
    assert row["delivery_month"] == "2609"


def test_json_provider_missing_data_list_is_failure():
    with pytest.raises(FinancialDataError):
        parse_dce_daily_payload({"result": 1}, "20260814", "u")


def test_cffex_csv_and_futures_filter_and_unit():
    text = (
        "合约代码,今开盘,最高价,最低价,成交量,成交金额,持仓量,持仓变化,今收盘,今结算,前结算,涨跌1,涨跌2\n"
        "IF2609,4000,4100,3950,100,12345,200,1,4050,4040,3990,60,50\n"
        "IO2609-C-4000,100,110,90,10,100,20,0,105,104,99,6,5\n"
        "小计,,,,,,,,,,,,\n"
    )
    rows = parse_cffex_daily_csv(text, "20260814", "u")
    assert len(rows) == 2
    assert rows[0]["turnover_unit"] == "CNY_10K"
    assert rows[0]["delivery_month"] == "2609"
    assert len(parse_cffex_daily_csv(text, "20260814", "u", futures_only=True)) == 1


def test_cffex_zip_parser():
    text = (
        "合约代码,今开盘,最高价,最低价,成交量,成交金额,持仓量,持仓变化,今收盘,今结算,前结算\n"
        "IF2609,4000,4100,3950,100,12345,200,1,4050,4040,3990\n"
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("20260814_1.csv", text.encode("gb2312"))
    row = parse_cffex_history_zip(buffer.getvalue(), "20260814", "u")[0]
    assert row["contract_id"] == "IF2609"
    assert row["delivery_month"] == "2609"


def test_czce_pipe_text_and_error_page():
    text = (
        "说明\n"
        "品种月份|昨结算|今开盘|最高价|最低价|今收盘|今结算|涨跌1|涨跌2|成交量(手)|空盘量|增减量|成交额(万元)|交割结算价\n"
        "CF609|15000|15100|15200|14900|15050|15040|50|40|1,234|5,678|10|9,999.5|\n"
        "小计|||||||||1234|5678||9999|\n"
    )
    row = parse_czce_daily_text(text, "20260814", "u")[0]
    assert row["contract_id"] == "CF609"
    assert row["delivery_month"] == "609"
    assert row["volume"] == 1234
    assert row["turnover_unit"] == "CNY_10K"
    with pytest.raises(FinancialDataError):
        parse_czce_daily_text("您的访问出错了", "20260814", "u")


def test_normalized_rows_feed_existing_analytics_without_glue():
    payload = {
        "o_curinstrument": [
            {
                "PRODUCTGROUPID": "cu", "DELIVERYMONTH": "2609",
                "OPENPRICE": 80000, "HIGHESTPRICE": 81000, "LOWESTPRICE": 79000,
                "CLOSEPRICE": 80500, "SETTLEMENTPRICE": 80300, "PRESETTLEMENTPRICE": 79800,
                "VOLUME": 123, "OPENINTEREST": 789, "TURNOVER": 456,
            },
            {
                "PRODUCTGROUPID": "cu", "DELIVERYMONTH": "2610",
                "OPENPRICE": 80100, "HIGHESTPRICE": 81100, "LOWESTPRICE": 79100,
                "CLOSEPRICE": 80600, "SETTLEMENTPRICE": 80400, "PRESETTLEMENTPRICE": 79900,
                "VOLUME": 100, "OPENINTEREST": 600, "TURNOVER": 400,
            },
        ]
    }
    rows = parse_shfe_daily_payload(payload, "20260814", "u")
    assert select_dominant_contract(rows)["contract_id"] == "CU2609"
    assert [item["contract_id"] for item in term_structure(rows)] == ["CU2609", "CU2610"]


def test_dispatcher_rejects_unknown_exchange():
    with pytest.raises(FinancialDataError) as exc:
        fetch_cn_futures_daily("NOPE", "20260814", client=None)
    assert exc.value.code == ErrorCode.FIELD_NOT_SUPPORTED
