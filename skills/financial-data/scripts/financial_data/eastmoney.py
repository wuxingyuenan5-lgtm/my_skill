from __future__ import annotations

import time
from typing import Callable, Iterable, Optional

from .adapters.base import HttpClient
from .contracts import ErrorCode, FinancialDataError
from .normalize import normalize_percentage


_DATACENTER = "https://datacenter-web.eastmoney.com/api/data/v1/get"
_PUSH2_LIST = "https://push2.eastmoney.com/api/qt/clist/get"
_SEARCH = "https://searchapi.eastmoney.com/api/suggest/get"
_SEARCH_TOKEN = "D43BF722C8E33BDC906FB84D85E326E8"
_MARKET_FS = {
    "us_nasdaq": "m:105",
    "us_nyse": "m:106",
    "us_etf": "m:107",
    "hk": "m:116",
    "cn_a": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
}
_MARKET_NAMES = {"105": "NASDAQ", "106": "NYSE", "107": "US_ETF", "116": "HK"}


def _number(value):
    if value in (None, "", "-"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class EastmoneyClient:
    """Reusable Eastmoney provider helper with conservative serial throttling."""

    def __init__(
        self,
        *,
        session=None,
        min_interval: float = 1.0,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.client = HttpClient(session=session)
        self.min_interval = max(0.0, float(min_interval))
        self.clock = clock
        self.sleeper = sleeper
        self._last_request: Optional[float] = None

    def _wait(self) -> None:
        now = self.clock()
        if self._last_request is not None and self.min_interval > 0:
            remaining = self.min_interval - (now - self._last_request)
            if remaining > 0:
                self.sleeper(remaining)
                now = self.clock()
        self._last_request = now

    def _json(self, url: str, *, params=None, headers=None):
        self._wait()
        return self.client.get_json(
            url,
            params=params or {},
            headers=headers or {"User-Agent": "Mozilla/5.0 financial-data"},
        )

    @staticmethod
    def _business_error(payload, *, family: str) -> None:
        if not isinstance(payload, dict):
            raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, f"Eastmoney {family} returned non-object JSON")
        if family == "datacenter":
            success = payload.get("success")
            code = payload.get("code")
            if success is False or code not in (None, 0, "0"):
                raise FinancialDataError(
                    ErrorCode.SOURCE_UNAVAILABLE,
                    "Eastmoney datacenter returned provider error",
                    {"code": code, "message": payload.get("message")},
                )
        elif family == "push2":
            rc = payload.get("rc", 0)
            if rc not in (0, "0", None):
                raise FinancialDataError(
                    ErrorCode.SOURCE_UNAVAILABLE,
                    "Eastmoney Push2 returned provider error",
                    {"rc": rc, "message": payload.get("message") or payload.get("msg")},
                )

    def datacenter_query(
        self,
        report_name: str,
        *,
        columns: str = "ALL",
        filter_str: str = "",
        page_number: int = 1,
        page_size: int = 50,
        sort_columns: str = "",
        sort_types: str = "-1",
        extra_params: Optional[dict] = None,
    ) -> dict:
        params = {
            "reportName": report_name,
            "columns": columns,
            "filter": filter_str,
            "pageNumber": str(page_number),
            "pageSize": str(page_size),
            "sortColumns": sort_columns,
            "sortTypes": sort_types,
            "source": "WEB",
            "client": "WEB",
        }
        if extra_params:
            params.update(extra_params)
        payload = self._json(_DATACENTER, params=params)
        self._business_error(payload, family="datacenter")
        result = payload.get("result")
        if result is None:
            return {"data": [], "count": 0, "pages": 0, "raw": payload}
        if not isinstance(result, dict):
            raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "Eastmoney datacenter result is not an object")
        data = result.get("data") or []
        if not isinstance(data, list):
            raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "Eastmoney datacenter data is not a list")
        return {
            "data": data,
            "count": int(result.get("count") or len(data)),
            "pages": int(result.get("pages") or 0),
            "raw": payload,
        }

    def push2_list(
        self,
        *,
        fs: str,
        fields: str = "f2,f3,f4,f5,f6,f7,f12,f14,f15,f16,f17,f18",
        page: int = 1,
        page_size: int = 20,
        sort_field: str = "f3",
        sort_desc: bool = True,
    ) -> dict:
        params = {
            "fs": fs,
            "fields": fields,
            "pn": page,
            "pz": page_size,
            "fid": sort_field,
            "po": 1 if sort_desc else 0,
        }
        payload = self._json(_PUSH2_LIST, params=params)
        self._business_error(payload, family="push2")
        data = payload.get("data")
        if data is None:
            raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "Eastmoney Push2 returned no data object", {"fs": fs})
        diff = data.get("diff") or []
        if isinstance(diff, dict):
            diff = list(diff.values())
        if not isinstance(diff, list):
            raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "Eastmoney Push2 diff is not a list")
        return {"total": int(data.get("total") or len(diff)), "rows": diff, "raw": payload}

    def market_stock_list(
        self,
        market: str = "us_nasdaq",
        sort_field: str = "f3",
        sort_desc: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        fs = _MARKET_FS.get(market, market)
        result = self.push2_list(fs=fs, page=page, page_size=page_size, sort_field=sort_field, sort_desc=sort_desc)
        stocks = []
        for row in result["rows"]:
            change_pct = _number(row.get("f3"))
            amplitude = _number(row.get("f7"))
            stocks.append({
                "code": str(row.get("f12") or ""),
                "name": row.get("f14"),
                "price": _number(row.get("f2")),
                "change_pct": normalize_percentage(change_pct, percent_points=True) if change_pct is not None else None,
                "change": _number(row.get("f4")),
                "volume": _number(row.get("f5")),
                "turnover": _number(row.get("f6")),
                "amplitude": normalize_percentage(amplitude, percent_points=True) if amplitude is not None else None,
                "high": _number(row.get("f15")),
                "low": _number(row.get("f16")),
                "open": _number(row.get("f17")),
                "previous_close": _number(row.get("f18")),
                "raw": row,
            })
        return {"market": market, "page": page, "total": result["total"], "stocks": stocks}

    def search_securities(
        self,
        keyword: str,
        *,
        count: int = 20,
        market_numbers: Iterable[str] = ("105", "106", "107", "116"),
    ) -> list[dict]:
        payload = self._json(_SEARCH, params={"input": keyword, "type": 14, "token": _SEARCH_TOKEN, "count": count})
        table = payload.get("QuotationCodeTable") or {}
        rows = table.get("Data") or []
        allowed = {str(value) for value in market_numbers}
        out = []
        for row in rows:
            mkt = str(row.get("MktNum") or "")
            if mkt not in allowed:
                continue
            out.append({
                "code": row.get("Code"),
                "name": row.get("Name"),
                "mkt_num": mkt,
                "market": _MARKET_NAMES.get(mkt, mkt),
                "security_type": row.get("SecurityTypeName") or row.get("SecurityType"),
                "raw": row,
            })
        return out
