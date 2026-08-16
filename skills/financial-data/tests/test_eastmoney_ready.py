import pytest

from financial_data.contracts import ErrorCode, FinancialDataError
from financial_data.eastmoney import EastmoneyClient


class Response:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code
        self.text = ""

    def json(self):
        return self.payload


class Session:
    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return Response(self.payloads.pop(0))


def test_datacenter_query_returns_data_and_count():
    session = Session([{"success": True, "code": 0, "result": {"count": 2, "pages": 1, "data": [{"A": 1}, {"A": 2}]}}])
    client = EastmoneyClient(session=session, min_interval=0)
    result = client.datacenter_query("RPT_TEST", filter_str='(CODE="x")')
    assert result["count"] == 2 and len(result["data"]) == 2
    assert session.calls[0][1]["params"]["reportName"] == "RPT_TEST"


def test_datacenter_business_error_is_not_empty_success():
    session = Session([{"success": False, "code": 9501, "message": "busy", "result": None}])
    client = EastmoneyClient(session=session, min_interval=0)
    with pytest.raises(FinancialDataError) as exc:
        client.datacenter_query("RPT_TEST")
    assert exc.value.code == ErrorCode.SOURCE_UNAVAILABLE


def test_market_stock_list_normalizes_percentages_and_preserves_raw():
    payload = {
        "rc": 0,
        "data": {
            "total": 1,
            "diff": [{"f12": "AAPL", "f14": "Apple", "f2": 200, "f3": 1.25, "f4": 2.5, "f5": 100, "f6": 20000, "f7": 2.0, "f15": 202, "f16": 198, "f17": 199, "f18": 197.5}],
        },
    }
    client = EastmoneyClient(session=Session([payload]), min_interval=0)
    result = client.market_stock_list("us_nasdaq")
    row = result["stocks"][0]
    assert row["change_pct"] == 0.0125 and row["amplitude"] == 0.02
    assert row["raw"]["f12"] == "AAPL"


def test_search_securities_filters_and_normalizes_us_hk_rows():
    payload = {
        "QuotationCodeTable": {
            "Data": [
                {"Code": "AAPL", "Name": "苹果", "MktNum": "105", "SecurityTypeName": "美股"},
                {"Code": "00700", "Name": "腾讯", "MktNum": "116", "SecurityTypeName": "港股"},
                {"Code": "600519", "Name": "茅台", "MktNum": "1"},
            ]
        }
    }
    client = EastmoneyClient(session=Session([payload]), min_interval=0)
    rows = client.search_securities("test")
    assert [row["market"] for row in rows] == ["NASDAQ", "HK"]
    assert rows[0]["raw"]["MktNum"] == "105"
