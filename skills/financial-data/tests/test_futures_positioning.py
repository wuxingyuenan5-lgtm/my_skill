import io
import zipfile

import pytest

from financial_data.contracts import ErrorCode, FinancialDataError
from financial_data.futures_positioning import (
    aggregate_standard_windows,
    aggregate_top_n,
    fetch_cn_futures_positions,
    make_ranking_fact,
    parse_cffex_position_csv,
    parse_czce_position_xlsx,
    parse_dce_position_zip,
    parse_gfex_position_pages,
    parse_ine_position_payload,
    parse_shfe_position_payload,
    position_denominators_from_daily,
    positioning_result,
    validate_ranking_fact,
)


def _fact(**overrides):
    base = dict(
        trade_date="20260814",
        exchange="SHFE",
        scope_type="contract",
        scope_id="CU2609",
        ranking_type="volume",
        rank=1,
        member="A期货",
        value=100,
        change=-3,
        source_url="https://example.com",
    )
    base.update(overrides)
    return make_ranking_fact(**base)


def test_fact_contract_and_status():
    row = _fact()
    assert row["trade_date"] == "2026-08-14"
    assert row["rank"] == 1
    assert row["change"] == -3
    assert validate_ranking_fact(row) == []
    with pytest.raises(FinancialDataError):
        _fact(ranking_type="bogus")
    assert positioning_result("SHFE", "20260814", "published", [row])["status"] == "published"
    with pytest.raises(ValueError):
        positioning_result("SHFE", "20260814", "unknown", [])


def test_shfe_long_form_does_not_fake_member_alignment():
    payload = {"o_cursor": [{
        "RANK": 1,
        "INSTRUMENTID": "cu2609",
        "PARTICIPANTABBR1": "成交A", "CJ1": "100", "CJ1_CHG": "10",
        "PARTICIPANTABBR2": "多头B", "CJ2": "80", "CJ2_CHG": "-2",
        "PARTICIPANTABBR3": "空头C", "CJ3": "70", "CJ3_CHG": "3",
    }]}
    result = parse_shfe_position_payload(payload, "20260814", "u")
    assert result["status"] == "published"
    assert [(row["ranking_type"], row["member"]) for row in result["rows"]] == [
        ("volume", "成交A"), ("long", "多头B"), ("short", "空头C")
    ]


def test_ine_parser_exists_but_dispatcher_not_ready():
    payload = {"o_cursor": [{
        "RANK": 1,
        "INSTRUMENTID": "sc2609",
        "PARTICIPANTABBR1": "A", "CJ1": 10, "CJ1_CHG": 1,
        "PARTICIPANTABBR2": "B", "CJ2": 9, "CJ2_CHG": 0,
        "PARTICIPANTABBR3": "C", "CJ3": 8, "CJ3_CHG": -1,
    }]}
    assert len(parse_ine_position_payload(payload, "20260814", "u")["rows"]) == 3
    with pytest.raises(FinancialDataError) as exc:
        fetch_cn_futures_positions("INE", "20260814")
    assert exc.value.code == ErrorCode.FIELD_NOT_SUPPORTED


def _dce_zip():
    text = """名次\t会员简称\t成交量\t增减
1\t成交A\t100\t10
2\t成交B\t90\t-5
总计\t\t190\t5
名次\t会员简称\t持买单量\t增减
1\t多A\t80\t2
2\t多B\t70\t-1
合计\t\t150\t1
名次\t会员简称\t持卖单量\t增减
1\t空A\t75\t3
2\t空B\t65\t-2
总计\t\t140\t1
"""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("20260814_m2609_成交量_买持仓_卖持仓排名.txt", text.encode("utf-8"))
    return buffer.getvalue()


def test_dce_zip_three_independent_sections():
    result = parse_dce_position_zip(_dce_zip(), "20260814", "u")
    assert result["status"] == "published"
    assert len(result["rows"]) == 6
    assert {row["ranking_type"] for row in result["rows"]} == {"volume", "long", "short"}
    assert {row["contract_id"] for row in result["rows"]} == {"M2609"}


def test_gfex_three_pages():
    pages = {
        1: {"data": [{"abbr": "成交A", "todayQty": "100", "todayQtyChg": "2"}]},
        2: {"data": [{"abbr": "多A", "todayQty": "80", "qtySub": "-1"}]},
        3: {"data": [{"abbr": "空A", "todayQty": "70", "todayQtyChg": "3"}]},
    }
    rows = parse_gfex_position_pages(
        pages, "20260814", "u", variety="lc", contract_id="lc2609"
    )["rows"]
    assert [(row["ranking_type"], row["member"]) for row in rows] == [
        ("volume", "成交A"), ("long", "多A"), ("short", "空A")
    ]


def test_cffex_current_positional_csv_fixture():
    text = """交易日,合约,名次,会员简称,成交量,增减,会员简称,持买单量,增减,会员简称,持卖单量,增减
20260814,IF2609,1,成交A,100,2,多A,80,-1,空A,70,3
"""
    rows = parse_cffex_position_csv(text, "20260814", "u")["rows"]
    assert len(rows) == 3
    assert rows[0]["contract_id"] == "IF2609"


def _xlsx_fixture():
    namespace = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    shared = [
        "CF609 合约", "名次", "会员简称", "成交量", "增减", "持买单量", "持卖单量",
        "成交A", "100", "2", "多A", "80", "-1", "空A", "70", "3", "合计", "1",
    ]
    sst = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<sst xmlns="{namespace}" count="{len(shared)}" uniqueCount="{len(shared)}">',
    ]
    for value in shared:
        sst.append(f"<si><t>{value}</t></si>")
    sst.append("</sst>")
    rows = [
        [0],
        [1, 2, 3, 4, 2, 5, 4, 2, 6, 4],
        [17, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        [16],
    ]
    sheet = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<worksheet xmlns="{namespace}"><sheetData>',
    ]
    for row_index, values in enumerate(rows, 1):
        sheet.append(f'<row r="{row_index}">')
        for column_index, value in enumerate(values):
            column = chr(ord("A") + column_index)
            sheet.append(f'<c r="{column}{row_index}" t="s"><v>{value}</v></c>')
        sheet.append("</row>")
    sheet.append("</sheetData></worksheet>")
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        archive.writestr("xl/sharedStrings.xml", "".join(sst))
        archive.writestr("xl/worksheets/sheet1.xml", "".join(sheet))
    return out.getvalue()


def test_czce_current_xlsx_parser():
    result = parse_czce_position_xlsx(_xlsx_fixture(), "20260814", "u")
    assert result["status"] == "published"
    assert {row["ranking_type"] for row in result["rows"]} == {"volume", "long", "short"}
    assert {row["contract_id"] for row in result["rows"]} == {"CF609"}


def test_topn_and_concentration_require_denominator():
    rows = []
    for rank in range(1, 7):
        rows += [
            _fact(ranking_type="volume", rank=rank, member=f"V{rank}", value=10),
            _fact(ranking_type="long", rank=rank, member=f"L{rank}", value=8),
            _fact(ranking_type="short", rank=rank, member=f"S{rank}", value=6),
        ]
    top5 = aggregate_top_n(rows, 5)
    assert top5["volume"] == 50
    assert top5["long_minus_short"] == 10
    assert top5["concentration"]["volume"] is None
    top5_with_denominator = aggregate_top_n(rows, 5, {"volume": 100, "open_interest": 80})
    assert top5_with_denominator["concentration"]["volume"] == 0.5
    assert top5_with_denominator["concentration"]["long"] == 0.5
    assert top5_with_denominator["concentration"]["short"] == 0.375
    assert set(aggregate_standard_windows(rows)) == {"top5", "top10", "top20"}


def test_denominator_bridge():
    daily = [{"contract_id": "CU2609", "volume": 1000, "open_interest": 800}]
    assert position_denominators_from_daily(daily, "cu2609") == {
        "volume": 1000.0,
        "open_interest": 800.0,
    }


class _Response:
    def __init__(self, content=b""):
        self.content = content


class _FakeClient:
    def __init__(self):
        self.calls = []

    def get_json(self, url, **kwargs):
        self.calls.append(("get_json", url, kwargs))
        return {"o_cursor": [{
            "RANK": 1,
            "INSTRUMENTID": "cu2609",
            "PARTICIPANTABBR1": "成交A", "CJ1": 100, "CJ1_CHG": 1,
            "PARTICIPANTABBR2": "多A", "CJ2": 80, "CJ2_CHG": 2,
            "PARTICIPANTABBR3": "空A", "CJ3": 70, "CJ3_CHG": 3,
        }]}

    def post_response(self, url, **kwargs):
        self.calls.append(("post_response", url, kwargs))
        return _Response(_dce_zip())

    def post_json(self, url, **kwargs):
        self.calls.append(("post_json", url, kwargs))
        if "loadListContract_id" in url:
            return {"data": [{"contract_id": "lc2609"}]}
        data_type = int(kwargs.get("data", {}).get("data_type", 1))
        names = {1: "成交A", 2: "多A", 3: "空A"}
        return {"data": [{"abbr": names[data_type], "todayQty": "10", "todayQtyChg": "1"}]}

    def get_response(self, url, **kwargs):
        self.calls.append(("get_response", url, kwargs))
        if "cffex" in url:
            content = (
                "交易日,合约,名次,会员简称,成交量,增减,会员简称,持买单量,增减,会员简称,持卖单量,增减\n"
                "20260814,IF2609,1,成交A,100,2,多A,80,-1,空A,70,3\n"
            ).encode("gbk")
            return _Response(content)
        return _Response(_xlsx_fixture())


def test_ready_fetcher_transports():
    from financial_data.futures_positioning import (
        fetch_cffex_positions,
        fetch_czce_positions,
        fetch_dce_positions,
        fetch_gfex_positions,
        fetch_shfe_positions,
    )

    client = _FakeClient()
    assert fetch_shfe_positions("20260814", client=client)["status"] == "published"
    assert fetch_dce_positions("20260814", client=client)["status"] == "published"
    assert fetch_gfex_positions("20260814", variety="lc", client=client)["status"] == "published"
    assert fetch_cffex_positions("20260814", product="IF", client=client)["status"] == "published"
    assert fetch_czce_positions("20260814", client=client)["status"] == "published"
