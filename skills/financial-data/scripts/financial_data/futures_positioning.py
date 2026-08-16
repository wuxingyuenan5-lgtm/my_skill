from __future__ import annotations

import csv
import io
import re
import zipfile
from datetime import date, datetime
from typing import Any, Dict, List, Mapping, Optional, Sequence
from xml.etree import ElementTree as ET

from .adapters.base import HttpClient
from .contracts import ErrorCode, FinancialDataError

RANKING_TYPES = {"volume", "long", "short"}
POSITION_STATUSES = {"published", "not_published_by_rule", "no_trading", "source_failure"}
SUMMARY_NAMES = {"合计", "总计", "小计", "会员类别"}


def normalize_trade_date(value: Any) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    if len(text) == 8 and text.isdigit():
        return f"{text[:4]}-{text[4:6]}-{text[6:8]}"
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError as exc:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, f"invalid trade_date: {value!r}") from exc


def _compact_date(value: Any) -> str:
    return normalize_trade_date(value).replace("-", "")


def _number(value: Any, *, integer: bool = False, allow_none: bool = False) -> Optional[float]:
    if value is None:
        if allow_none:
            return None
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "numeric ranking value is missing")
    if isinstance(value, str):
        value = value.strip().replace(",", "")
        if value in {"", "-", "--"}:
            if allow_none:
                return None
            value = "0"
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, f"invalid numeric ranking value: {value!r}") from exc
    return int(number) if integer else number


def _variety(scope_id: str) -> Optional[str]:
    match = re.match(r"([A-Za-z]+)", str(scope_id).strip())
    return match.group(1).upper() if match else None


def validate_ranking_fact(row: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    for key in (
        "trade_date", "exchange", "scope_type", "scope_id", "ranking_type",
        "rank", "member", "value", "source_id", "source_url",
    ):
        if row.get(key) in (None, ""):
            errors.append(f"missing {key}")
    if row.get("ranking_type") not in RANKING_TYPES:
        errors.append("unsupported ranking_type")
    if row.get("scope_type") not in {"contract", "product"}:
        errors.append("unsupported scope_type")
    try:
        if int(row.get("rank", 0)) <= 0:
            errors.append("rank must be positive")
    except (TypeError, ValueError):
        errors.append("rank must be integer")
    try:
        if float(row.get("value", -1)) < 0:
            errors.append("value cannot be negative")
    except (TypeError, ValueError):
        errors.append("value must be numeric")
    change = row.get("change")
    if change is not None:
        try:
            float(change)
        except (TypeError, ValueError):
            errors.append("change must be numeric when present")
    if row.get("scope_type") == "contract" and not row.get("contract_id"):
        errors.append("contract scope requires contract_id")
    return errors


def make_ranking_fact(
    *,
    trade_date: Any,
    exchange: str,
    scope_type: str,
    scope_id: str,
    ranking_type: str,
    rank: Any,
    member: Any,
    value: Any,
    change: Any = None,
    variety: Optional[str] = None,
    contract_id: Optional[str] = None,
    source_id: Optional[str] = None,
    source_url: str,
    raw: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    scope = str(scope_id).strip().upper()
    row: Dict[str, Any] = {
        "trade_date": normalize_trade_date(trade_date),
        "exchange": str(exchange).strip().upper(),
        "scope_type": str(scope_type).strip().lower(),
        "scope_id": scope,
        "variety": (variety or _variety(scope) or "").upper() or None,
        "contract_id": contract_id or (scope if scope_type == "contract" else None),
        "ranking_type": str(ranking_type).strip().lower(),
        "rank": _number(rank, integer=True),
        "member": str(member).strip(),
        "value": _number(value),
        "change": _number(change, allow_none=True),
        "source_id": source_id or str(exchange).strip().lower(),
        "source_url": source_url,
    }
    if row["contract_id"]:
        row["contract_id"] = str(row["contract_id"]).strip().upper()
    if raw is not None:
        row["raw"] = dict(raw)
    errors = validate_ranking_fact(row)
    if errors:
        raise FinancialDataError(
            ErrorCode.VALIDATION_FAILED,
            "invalid futures positioning fact",
            {"issues": errors, "row": row},
        )
    return row


def positioning_result(
    exchange: str,
    trade_date: Any,
    status: str,
    rows: Sequence[Mapping[str, Any]],
    *,
    source_id: Optional[str] = None,
    source_url: Optional[str] = None,
    details: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    if status not in POSITION_STATUSES:
        raise ValueError(f"unsupported positioning status: {status}")
    return {
        "exchange": str(exchange).upper(),
        "trade_date": normalize_trade_date(trade_date),
        "status": status,
        "rows": [dict(row) for row in rows],
        "source_id": source_id or str(exchange).lower(),
        "source_url": source_url,
        "details": dict(details or {}),
    }


def _emit_wide_row(
    raw: Mapping[str, Any],
    *,
    trade_date: Any,
    exchange: str,
    scope_type: str,
    scope_id: str,
    source_url: str,
    source_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    rank = raw.get("rank", raw.get("RANK"))
    specs = (
        ("volume", raw.get("vol_party_name", raw.get("PARTICIPANTABBR1")), raw.get("vol", raw.get("CJ1")), raw.get("vol_chg", raw.get("CJ1_CHG"))),
        ("long", raw.get("long_party_name", raw.get("PARTICIPANTABBR2")), raw.get("long_open_interest", raw.get("CJ2")), raw.get("long_open_interest_chg", raw.get("CJ2_CHG"))),
        ("short", raw.get("short_party_name", raw.get("PARTICIPANTABBR3")), raw.get("short_open_interest", raw.get("CJ3")), raw.get("short_open_interest_chg", raw.get("CJ3_CHG"))),
    )
    out: List[Dict[str, Any]] = []
    for ranking_type, member, value, change in specs:
        if member in (None, "") or value in (None, ""):
            continue
        if str(member).strip() in SUMMARY_NAMES:
            continue
        out.append(make_ranking_fact(
            trade_date=trade_date,
            exchange=exchange,
            scope_type=scope_type,
            scope_id=scope_id,
            ranking_type=ranking_type,
            rank=rank,
            member=member,
            value=value,
            change=change,
            variety=_variety(scope_id),
            contract_id=scope_id if scope_type == "contract" else None,
            source_id=source_id,
            source_url=source_url,
            raw=raw,
        ))
    return out


def _parse_cursor_payload(
    payload: Any,
    *,
    trade_date: Any,
    exchange: str,
    source_url: str,
    source_id: str,
) -> Dict[str, Any]:
    if not isinstance(payload, Mapping) or not isinstance(payload.get("o_cursor"), list):
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, f"{exchange} positioning payload missing o_cursor")
    facts: List[Dict[str, Any]] = []
    for raw in payload["o_cursor"]:
        if not isinstance(raw, Mapping):
            continue
        try:
            if int(raw.get("RANK") or 0) <= 0:
                continue
        except (TypeError, ValueError):
            continue
        scope_id = str(raw.get("INSTRUMENTID") or "").strip().upper()
        if not scope_id:
            continue
        facts.extend(_emit_wide_row(
            raw,
            trade_date=trade_date,
            exchange=exchange,
            scope_type="contract",
            scope_id=scope_id,
            source_url=source_url,
            source_id=source_id,
        ))
    status = "published" if facts else "not_published_by_rule"
    return positioning_result(
        exchange,
        trade_date,
        status,
        facts,
        source_id=source_id,
        source_url=source_url,
        details={"empty_payload_status_inferred": not bool(facts)},
    )


def parse_shfe_position_payload(payload: Any, trade_date: Any, source_url: str) -> Dict[str, Any]:
    return _parse_cursor_payload(payload, trade_date=trade_date, exchange="SHFE", source_url=source_url, source_id="shfe")


def parse_ine_position_payload(payload: Any, trade_date: Any, source_url: str) -> Dict[str, Any]:
    return _parse_cursor_payload(payload, trade_date=trade_date, exchange="INE", source_url=source_url, source_id="ine")


def fetch_shfe_positions(trade_date: Any, *, client: Optional[HttpClient] = None) -> Dict[str, Any]:
    compact = _compact_date(trade_date)
    url = f"https://www.shfe.com.cn/data/tradedata/future/dailydata/pm{compact}.dat"
    http = client or HttpClient(timeout=15.0, max_retries=2)
    return parse_shfe_position_payload(http.get_json(url), trade_date, url)


def _decode_bytes(content: bytes, encodings: Sequence[str]) -> str:
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            pass
    raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "cannot decode provider payload")


def _parse_rank_sections(
    text: str,
    *,
    trade_date: Any,
    exchange: str,
    contract_id: str,
    source_url: str,
) -> List[Dict[str, Any]]:
    facts: List[Dict[str, Any]] = []
    section = -1
    ranking_types = ["volume", "long", "short"]
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^名次", stripped):
            section += 1
            continue
        if section < 0 or section > 2 or re.match(r"^(?:总计|合计)", stripped):
            continue
        cells = [cell.strip() for cell in re.split(r"\t+|\s{2,}", stripped) if cell.strip()]
        if len(cells) < 3:
            continue
        try:
            rank = int(float(cells[0]))
        except ValueError:
            continue
        facts.append(make_ranking_fact(
            trade_date=trade_date,
            exchange=exchange,
            scope_type="contract",
            scope_id=contract_id,
            ranking_type=ranking_types[section],
            rank=rank,
            member=cells[1],
            value=cells[2],
            change=cells[3] if len(cells) > 3 else None,
            source_url=source_url,
            raw={"line": line},
        ))
    return facts


def parse_dce_position_zip(content: bytes, trade_date: Any, source_url: str) -> Dict[str, Any]:
    facts: List[Dict[str, Any]] = []
    compact = _compact_date(trade_date)
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            for name in archive.namelist():
                base = name.split("/")[-1]
                if not base.startswith(compact + "_"):
                    continue
                parts = base.split("_")
                if len(parts) < 2:
                    continue
                contract_id = parts[1].upper()
                text = _decode_bytes(archive.read(name), ("utf-8-sig", "gb18030", "gb2312"))
                facts.extend(_parse_rank_sections(
                    text,
                    trade_date=trade_date,
                    exchange="DCE",
                    contract_id=contract_id,
                    source_url=source_url,
                ))
    except FinancialDataError:
        raise
    except Exception as exc:
        raise FinancialDataError(
            ErrorCode.NORMALIZATION_ERROR,
            f"invalid DCE positioning ZIP: {exc}",
            {"source_url": source_url},
        ) from exc
    return positioning_result(
        "DCE",
        trade_date,
        "published" if facts else "not_published_by_rule",
        facts,
        source_id="dce",
        source_url=source_url,
        details={"empty_payload_status_inferred": not bool(facts)},
    )


def fetch_dce_positions(trade_date: Any, *, client: Optional[HttpClient] = None) -> Dict[str, Any]:
    compact = _compact_date(trade_date)
    url = "https://www.dce.com.cn/dcereport/publicweb/dailystat/memberDealPosi/batchDownload"
    payload = {"tradeDate": compact, "varietyId": "a", "contractId": "", "tradeType": "1", "lang": "zh"}
    http = client or HttpClient(timeout=20.0, max_retries=2)
    response = http.post_response(url, json=payload)
    content = bytes(getattr(response, "content", b""))
    if not content:
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "DCE positioning ZIP is empty", {"source_url": url})
    return parse_dce_position_zip(content, trade_date, url)


def parse_gfex_position_pages(
    pages: Mapping[int, Any],
    trade_date: Any,
    source_url: str,
    *,
    variety: str,
    contract_id: str,
) -> Dict[str, Any]:
    facts: List[Dict[str, Any]] = []
    mapping = {1: "volume", 2: "long", 3: "short"}
    for data_type, ranking_type in mapping.items():
        payload = pages.get(data_type)
        if not isinstance(payload, Mapping) or not isinstance(payload.get("data"), list):
            raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, f"GFEX positioning page {data_type} missing data")
        for index, raw in enumerate(payload["data"], 1):
            if not isinstance(raw, Mapping):
                continue
            member = str(raw.get("abbr") or "").strip()
            if not member or member in SUMMARY_NAMES or raw.get("todayQty") in (None, ""):
                continue
            change = raw.get("qtySub")
            if change in (None, ""):
                change = raw.get("todayQtyChg")
            facts.append(make_ranking_fact(
                trade_date=trade_date,
                exchange="GFEX",
                scope_type="contract",
                scope_id=contract_id,
                variety=variety,
                contract_id=contract_id,
                ranking_type=ranking_type,
                rank=raw.get("rank") or raw.get("ranking") or index,
                member=member,
                value=raw.get("todayQty"),
                change=change,
                source_id="gfex",
                source_url=source_url,
                raw=raw,
            ))
    return positioning_result(
        "GFEX",
        trade_date,
        "published" if facts else "not_published_by_rule",
        facts,
        source_id="gfex",
        source_url=source_url,
    )


def _extract_contract_ids(payload: Any) -> List[str]:
    if not isinstance(payload, Mapping) or not isinstance(payload.get("data"), list):
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "GFEX contract-list payload missing data")
    out: List[str] = []
    for row in payload["data"]:
        if isinstance(row, Mapping):
            value = row.get("contract_id") or row.get("contractId") or row.get("contract") or next(iter(row.values()), None)
        else:
            value = row
        if value not in (None, ""):
            out.append(str(value).strip())
    return out


def fetch_gfex_positions(
    trade_date: Any,
    *,
    variety: str,
    contract_id: Optional[str] = None,
    client: Optional[HttpClient] = None,
) -> Dict[str, Any]:
    if not variety:
        raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, "GFEX positioning fetch requires variety")
    compact = _compact_date(trade_date)
    http = client or HttpClient(timeout=15.0, max_retries=2)
    contracts = [contract_id] if contract_id else []
    if not contracts:
        list_url = "https://www.gfex.com.cn/u/interfacesWebTiMemberDealPosiQuotes/loadListContract_id"
        contracts = _extract_contract_ids(http.post_json(list_url, data={"variety": variety.lower(), "trade_date": compact}))
    all_rows: List[Dict[str, Any]] = []
    source_url = "https://www.gfex.com.cn/u/interfacesWebTiMemberDealPosiQuotes/loadList"
    for cid in contracts:
        pages: Dict[int, Any] = {}
        for data_type in (1, 2, 3):
            pages[data_type] = http.post_json(source_url, data={
                "trade_date": compact,
                "trade_type": "0",
                "variety": variety.lower(),
                "contract_id": cid,
                "data_type": str(data_type),
            })
        all_rows.extend(parse_gfex_position_pages(
            pages,
            trade_date,
            source_url,
            variety=variety,
            contract_id=str(cid),
        )["rows"])
    return positioning_result(
        "GFEX",
        trade_date,
        "published" if all_rows else "not_published_by_rule",
        all_rows,
        source_id="gfex",
        source_url="https://www.gfex.com.cn/gfex/rcjccpm/hqsj_tjsj.shtml",
    )


def parse_cffex_position_csv(text: str, trade_date: Any, source_url: str) -> Dict[str, Any]:
    if "合约" not in text:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "CFFEX positioning CSV header not recognized")
    rows = list(csv.reader(line for line in text.lstrip("\ufeff").splitlines() if line.strip()))
    header_index = next((i for i, row in enumerate(rows) if "交易日" in row and any("合约" in cell for cell in row)), None)
    if header_index is None:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "CFFEX positioning CSV header not recognized")
    facts: List[Dict[str, Any]] = []
    for cells in rows[header_index + 1:]:
        cells = [str(cell).strip() for cell in cells]
        if len(cells) < 12:
            continue
        contract_id = cells[1].upper()
        if not contract_id or contract_id in SUMMARY_NAMES:
            continue
        wide = {
            "rank": cells[2],
            "vol_party_name": cells[3], "vol": cells[4], "vol_chg": cells[5],
            "long_party_name": cells[6], "long_open_interest": cells[7], "long_open_interest_chg": cells[8],
            "short_party_name": cells[9], "short_open_interest": cells[10], "short_open_interest_chg": cells[11],
        }
        try:
            facts.extend(_emit_wide_row(
                wide,
                trade_date=trade_date,
                exchange="CFFEX",
                scope_type="contract",
                scope_id=contract_id,
                source_url=source_url,
                source_id="cffex",
            ))
        except FinancialDataError:
            continue
    return positioning_result(
        "CFFEX",
        trade_date,
        "published" if facts else "not_published_by_rule",
        facts,
        source_id="cffex",
        source_url=source_url,
    )


def fetch_cffex_positions(
    trade_date: Any,
    *,
    product: str,
    client: Optional[HttpClient] = None,
) -> Dict[str, Any]:
    if not product:
        raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, "CFFEX positioning fetch requires product code")
    compact = _compact_date(trade_date)
    url = f"https://www.cffex.com.cn/sj/ccpm/{compact[:6]}/{compact[6:8]}/{str(product).upper()}_1.csv"
    http = client or HttpClient(timeout=15.0, max_retries=2)
    response = http.get_response(url, headers={"User-Agent": "Mozilla/5.0 financial-data/0.2.3"})
    content = bytes(getattr(response, "content", b""))
    if not content:
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "CFFEX positioning CSV is empty", {"source_url": url})
    return parse_cffex_position_csv(_decode_bytes(content, ("gb18030", "gbk", "utf-8-sig")), trade_date, url)


def _xlsx_rows(content: bytes) -> List[List[str]]:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            shared: List[str] = []
            namespace = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            if "xl/sharedStrings.xml" in archive.namelist():
                root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
                for item in root.findall("a:si", namespace):
                    shared.append("".join(node.text or "" for node in item.iterfind(".//a:t", namespace)))
            sheet_name = next((name for name in archive.namelist() if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")), None)
            if not sheet_name:
                raise ValueError("xlsx has no worksheet")
            sheet = ET.fromstring(archive.read(sheet_name))
            out: List[List[str]] = []
            for row in sheet.findall(".//a:row", namespace):
                values: List[str] = []
                for cell in row.findall("a:c", namespace):
                    ref = cell.attrib.get("r", "")
                    letters = "".join(ch for ch in ref if ch.isalpha())
                    column = 0
                    for ch in letters.upper():
                        column = column * 26 + (ord(ch) - 64)
                    column = max(column - 1, len(values))
                    while len(values) < column:
                        values.append("")
                    value_node = cell.find("a:v", namespace)
                    inline_node = cell.find("a:is/a:t", namespace)
                    if inline_node is not None:
                        value = inline_node.text or ""
                    elif value_node is None or value_node.text is None:
                        value = ""
                    elif cell.attrib.get("t") == "s":
                        value = shared[int(value_node.text)]
                    else:
                        value = value_node.text or ""
                    if len(values) == column:
                        values.append(value)
                    else:
                        values[column] = value
                out.append(values)
            return out
    except Exception as exc:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, f"invalid CZCE xlsx: {exc}") from exc


def parse_czce_position_xlsx(content: bytes, trade_date: Any, source_url: str) -> Dict[str, Any]:
    facts: List[Dict[str, Any]] = []
    current_scope: Optional[str] = None
    header_seen = False
    for cells in _xlsx_rows(content):
        cells = [str(value).strip() for value in cells]
        if not any(cells):
            continue
        first = cells[0]
        contract_match = re.search(r"([A-Za-z]{1,3}\d{3,4})", first)
        if contract_match and ("品种" in first or "合约" in first or len(cells) == 1):
            current_scope = contract_match.group(1).upper()
            header_seen = False
            continue
        if first in {"名次", "排名"} or ("会员简称" in cells and ("成交量" in cells or "持买单量" in cells)):
            header_seen = True
            continue
        if "合计" in first or "总计" in first:
            header_seen = False
            continue
        if not current_scope or not header_seen or len(cells) < 10:
            continue
        wide = {
            "rank": cells[0],
            "vol_party_name": cells[1], "vol": cells[2], "vol_chg": cells[3],
            "long_party_name": cells[4], "long_open_interest": cells[5], "long_open_interest_chg": cells[6],
            "short_party_name": cells[7], "short_open_interest": cells[8], "short_open_interest_chg": cells[9],
        }
        try:
            facts.extend(_emit_wide_row(
                wide,
                trade_date=trade_date,
                exchange="CZCE",
                scope_type="contract",
                scope_id=current_scope,
                source_url=source_url,
                source_id="czce",
            ))
        except FinancialDataError:
            continue
    return positioning_result(
        "CZCE",
        trade_date,
        "published" if facts else "not_published_by_rule",
        facts,
        source_id="czce",
        source_url=source_url,
    )


def fetch_czce_positions(trade_date: Any, *, client: Optional[HttpClient] = None) -> Dict[str, Any]:
    compact = _compact_date(trade_date)
    if int(compact) < 20251102:
        raise FinancialDataError(
            ErrorCode.FIELD_NOT_SUPPORTED,
            "CZCE READY positioning fetch supports current XLSX regime from 2025-11-02",
        )
    url = f"https://www.czce.com.cn/cn/DFSStaticFiles/Future/{compact[:4]}/{compact}/FutureDataHolding.xlsx"
    http = client or HttpClient(timeout=20.0, max_retries=2)
    response = http.get_response(url, headers={"User-Agent": "Mozilla/5.0 financial-data/0.2.3"})
    content = bytes(getattr(response, "content", b""))
    if not content:
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "CZCE positioning XLSX is empty", {"source_url": url})
    return parse_czce_position_xlsx(content, trade_date, url)


def aggregate_top_n(
    rows: Sequence[Mapping[str, Any]],
    n: int,
    denominator: Optional[Mapping[str, float]] = None,
) -> Dict[str, Any]:
    if n <= 0:
        raise ValueError("n must be positive")
    if not rows:
        return {
            "n": n,
            "volume": 0.0, "volume_change": 0.0,
            "long": 0.0, "long_change": 0.0,
            "short": 0.0, "short_change": 0.0,
            "long_minus_short": 0.0,
            "concentration": {},
        }
    scopes = {(row.get("exchange"), row.get("trade_date"), row.get("scope_type"), row.get("scope_id")) for row in rows}
    if len(scopes) != 1:
        raise ValueError("aggregate_top_n requires one exchange/trade_date/scope")
    sums = {"volume": 0.0, "long": 0.0, "short": 0.0}
    changes = {"volume": 0.0, "long": 0.0, "short": 0.0}
    for row in rows:
        if int(row["rank"]) > n:
            continue
        ranking_type = row["ranking_type"]
        sums[ranking_type] += float(row["value"])
        if row.get("change") is not None:
            changes[ranking_type] += float(row["change"])
    concentration: Dict[str, Optional[float]] = {}
    denominators = dict(denominator or {})
    for ranking_type in ("volume", "long", "short"):
        denominator_key = "volume" if ranking_type == "volume" else "open_interest"
        denominator_value = denominators.get(denominator_key)
        concentration[ranking_type] = (
            sums[ranking_type] / float(denominator_value)
            if denominator_value is not None and float(denominator_value) > 0
            else None
        )
    return {
        "n": n,
        "volume": sums["volume"], "volume_change": changes["volume"],
        "long": sums["long"], "long_change": changes["long"],
        "short": sums["short"], "short_change": changes["short"],
        "long_minus_short": sums["long"] - sums["short"],
        "concentration": concentration,
    }


def aggregate_standard_windows(
    rows: Sequence[Mapping[str, Any]],
    denominators: Optional[Mapping[str, float]] = None,
) -> Dict[str, Any]:
    return {f"top{n}": aggregate_top_n(rows, n, denominators) for n in (5, 10, 20)}


def position_denominators_from_daily(rows: Sequence[Mapping[str, Any]], contract_id: str) -> Dict[str, float]:
    target = str(contract_id).strip().upper()
    matches = [row for row in rows if str(row.get("contract_id", "")).upper() == target]
    if len(matches) != 1:
        raise ValueError(f"expected one daily row for {target}, got {len(matches)}")
    row = matches[0]
    out: Dict[str, float] = {}
    if row.get("volume") is not None:
        out["volume"] = float(row["volume"])
    if row.get("open_interest") is not None:
        out["open_interest"] = float(row["open_interest"])
    return out


_FETCHERS = {
    "SHFE": fetch_shfe_positions,
    "DCE": fetch_dce_positions,
    "CZCE": fetch_czce_positions,
    "CFFEX": fetch_cffex_positions,
    "GFEX": fetch_gfex_positions,
}


def fetch_cn_futures_positions(exchange: str, trade_date: Any, **kwargs: Any) -> Dict[str, Any]:
    key = str(exchange).strip().upper()
    if key not in _FETCHERS:
        if key == "INE":
            raise FinancialDataError(
                ErrorCode.FIELD_NOT_SUPPORTED,
                "INE positioning parser exists, but current machine fetch path is not frozen as READY",
            )
        raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"unsupported China futures positioning exchange: {exchange}")
    return _FETCHERS[key](trade_date, **kwargs)


__all__ = [
    "make_ranking_fact", "validate_ranking_fact", "positioning_result",
    "parse_shfe_position_payload", "parse_ine_position_payload", "fetch_shfe_positions",
    "parse_dce_position_zip", "fetch_dce_positions",
    "parse_gfex_position_pages", "fetch_gfex_positions",
    "parse_cffex_position_csv", "fetch_cffex_positions",
    "parse_czce_position_xlsx", "fetch_czce_positions",
    "aggregate_top_n", "aggregate_standard_windows", "position_denominators_from_daily",
    "fetch_cn_futures_positions",
]
