from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

COT_LEGACY_FUTURES_ONLY = "https://publicreporting.cftc.gov/resource/6dca-aqww.json"


def build_cot_query(limit: int = 20, market_contains: Optional[str] = None) -> Dict[str, Any]:
    if limit < 1 or limit > 50000:
        raise ValueError("limit must be between 1 and 50000")
    query: Dict[str, Any] = {"$limit": int(limit), "$order": "report_date_as_yyyy_mm_dd DESC"}
    if market_contains:
        safe = str(market_contains).replace("'", "''").upper()
        query["$where"] = "upper(contract_market_name) like '%{}%'".format(safe)
    return query


def _int_or_none(value: Any):
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def parse_cot_rows(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for row in rows:
        report_date = str(row.get("report_date_as_yyyy_mm_dd") or "")[:10] or None
        out.append({
            "report_date": report_date,
            "market": row.get("contract_market_name"),
            "cftc_contract_code": row.get("cftc_contract_market_code"),
            "open_interest": _int_or_none(row.get("open_interest_all")),
            "raw": dict(row),
        })
    return out


def fetch_cot(limit: int = 20, market_contains: Optional[str] = None, *, dataset_url: str = COT_LEGACY_FUTURES_ONLY, session=None, timeout: int = 15) -> List[Dict[str, Any]]:
    import requests
    client = session or requests.Session()
    response = client.get(dataset_url, params=build_cot_query(limit, market_contains), timeout=timeout, headers={"User-Agent": "financial-data/0.2.0"})
    response.raise_for_status()
    return parse_cot_rows(response.json())
