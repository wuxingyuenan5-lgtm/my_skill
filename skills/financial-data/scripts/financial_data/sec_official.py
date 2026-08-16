from __future__ import annotations

from datetime import date
import os
from typing import Any, Dict, List, Optional


def _sec_headers(contact: Optional[str] = None) -> Dict[str, str]:
    value = (contact or os.environ.get("SEC_CONTACT", "")).strip()
    if not value or "@" not in value:
        raise ValueError("SEC_CONTACT must contain a truthful name/email")
    return {"User-Agent": "financial-data/0.2.0 (%s)" % value, "Accept-Encoding": "gzip, deflate"}


def sec_frame_url(taxonomy: str, tag: str, unit: str, period: str) -> str:
    return "https://data.sec.gov/api/xbrl/frames/{}/{}/{}/{}.json".format(taxonomy, tag, unit, period)


def parse_sec_frame_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for row in payload.get("data") or []:
        cik_raw = row.get("cik")
        cik = str(cik_raw).zfill(10) if cik_raw is not None else None
        rows.append({
            "cik": cik,
            "entity": row.get("entityName"),
            "location": row.get("loc"),
            "end": row.get("end"),
            "value": row.get("val"),
            "accession": row.get("accn"),
            "fy": row.get("fy"),
            "fp": row.get("fp"),
            "form": row.get("form"),
            "filed": row.get("filed"),
            "frame": row.get("frame"),
        })
    return {
        "taxonomy": payload.get("taxonomy"),
        "tag": payload.get("tag"),
        "label": payload.get("label"),
        "description": payload.get("description"),
        "period": payload.get("ccp") or (rows[0].get("frame") if rows else None),
        "unit": payload.get("uom"),
        "count": len(rows),
        "data": rows,
    }


def fetch_sec_frame(taxonomy: str, tag: str, unit: str, period: str, *, session=None, contact: Optional[str] = None, timeout: int = 15) -> Dict[str, Any]:
    import requests
    client = session or requests.Session()
    response = client.get(sec_frame_url(taxonomy, tag, unit, period), headers=_sec_headers(contact), timeout=timeout)
    response.raise_for_status()
    return parse_sec_frame_payload(response.json())


def sec_master_index_url(day: date) -> str:
    quarter = (day.month - 1) // 3 + 1
    return "https://www.sec.gov/Archives/edgar/daily-index/{}/QTR{}/master.{}.idx".format(day.year, quarter, day.strftime("%Y%m%d"))


def parse_sec_master_index(text: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for line in text.splitlines():
        parts = line.split("|")
        if len(parts) != 5 or not parts[0].strip().isdigit():
            continue
        rows.append({
            "cik": parts[0].strip().zfill(10),
            "company": parts[1].strip(),
            "form": parts[2].strip(),
            "filed": parts[3].strip(),
            "filename": parts[4].strip(),
        })
    return rows


def fetch_sec_master_index(day: date, *, session=None, contact: Optional[str] = None, timeout: int = 15) -> List[Dict[str, str]]:
    import requests
    client = session or requests.Session()
    response = client.get(sec_master_index_url(day), headers=_sec_headers(contact), timeout=timeout)
    response.raise_for_status()
    return parse_sec_master_index(response.text)
