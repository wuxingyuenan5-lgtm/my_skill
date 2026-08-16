from __future__ import annotations

import csv
import io
import re
import zipfile
from datetime import date, datetime
from typing import Any, Callable, Optional, Union

from .adapters.base import HttpClient
from .contracts import ErrorCode, FinancialDataError


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


def _num(value: Any, *, integer: bool = False) -> Optional[Union[float, int]]:
    if value is None or value == "":
        return None
    if isinstance(value, str):
        value = value.strip().replace(",", "")
        if value in {"", "-", "--"}:
            return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, f"invalid numeric futures value: {value!r}") from exc
    return int(number) if integer else number


def _variety(contract_id: str) -> str:
    match = re.match(r"([A-Za-z]+)", str(contract_id).strip())
    if not match:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, f"cannot infer futures variety from {contract_id!r}")
    return match.group(1).upper()


def _delivery_month(contract_id: str) -> Optional[str]:
    match = re.match(r"[A-Za-z]+([0-9]{3,4})", str(contract_id).strip())
    return match.group(1) if match else None


def validate_futures_daily_row(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("contract_id", "trade_date"):
        if not row.get(key):
            errors.append(f"VALIDATION_FAILED: missing {key}")
    o, h, l, c = (row.get(k) for k in ("open", "high", "low", "close"))
    if all(v is not None for v in (o, h, l, c)):
        of, hf, lf, cf = map(float, (o, h, l, c))
        if hf < max(of, lf, cf):
            errors.append("VALIDATION_FAILED: high is below open/low/close")
        if lf > min(of, hf, cf):
            errors.append("VALIDATION_FAILED: low is above open/high/close")
    for key in ("volume", "open_interest", "turnover"):
        value = row.get(key)
        if value is not None and float(value) < 0:
            errors.append(f"VALIDATION_FAILED: {key} cannot be negative")
    return errors


def _canonical_row(
    *, contract_id: str, variety: Optional[str], exchange: str, trade_date: Any,
    open_: Any, high: Any, low: Any, close: Any, settlement: Any, pre_settlement: Any,
    volume: Any, turnover: Any, open_interest: Any, source_id: str, source_url: str,
    currency: str = "CNY", volume_unit: str = "contracts", turnover_unit: str = "provider_declared",
    raw: Optional[dict[str, Any]] = None, **extra: Any,
) -> dict[str, Any]:
    cid = str(contract_id).strip().upper()
    row = {
        "contract_id": cid,
        "variety": (variety or _variety(cid)).strip().upper(),
        "exchange": exchange.upper(),
        "trade_date": normalize_trade_date(trade_date),
        "open": _num(open_), "high": _num(high), "low": _num(low), "close": _num(close),
        "settlement": _num(settlement), "pre_settlement": _num(pre_settlement),
        "volume": _num(volume, integer=True), "turnover": _num(turnover),
        "open_interest": _num(open_interest, integer=True), "currency": currency,
        "volume_unit": volume_unit, "turnover_unit": turnover_unit,
        "source_id": source_id, "source_url": source_url,
    }
    if raw is not None:
        row["raw"] = raw
    row.update(extra)
    errors = validate_futures_daily_row(row)
    if errors:
        raise FinancialDataError(ErrorCode.VALIDATION_FAILED, "invalid futures daily row", {"issues": errors, "row": row})
    return row


def _structured_exchange_rows(payload: Any, *, trade_date: Any, exchange: str, source_id: str, source_url: str) -> list[dict[str, Any]]:
    if not isinstance(payload, dict) or "o_curinstrument" not in payload or not isinstance(payload["o_curinstrument"], list):
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, f"{exchange} daily payload missing o_curinstrument")
    out = []
    for raw in payload["o_curinstrument"]:
        if not isinstance(raw, dict):
            continue
        delivery = str(raw.get("DELIVERYMONTH", "")).strip()
        product_name = str(raw.get("PRODUCTNAME", "")).strip()
        if delivery in {"", "小计", "合计", "总计"} or "总计" in product_name:
            continue
        product = str(raw.get("PRODUCTGROUPID") or raw.get("PRODUCTID") or "").strip()
        product = product.split("_")[0].strip().upper()
        if not product:
            raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, f"{exchange} row missing product code", {"row": raw})
        contract = product + delivery
        if "EFP" in contract.upper():
            continue
        out.append(_canonical_row(
            contract_id=contract, variety=product, exchange=exchange, trade_date=trade_date,
            open_=raw.get("OPENPRICE"), high=raw.get("HIGHESTPRICE"), low=raw.get("LOWESTPRICE"), close=raw.get("CLOSEPRICE"),
            settlement=raw.get("SETTLEMENTPRICE"), pre_settlement=raw.get("PRESETTLEMENTPRICE"), volume=raw.get("VOLUME"),
            turnover=raw.get("TURNOVER"), open_interest=raw.get("OPENINTEREST"), source_id=source_id, source_url=source_url,
            turnover_unit="provider_declared", raw=raw, delivery_month=delivery,
        ))
    return out


def parse_shfe_daily_payload(payload: Any, trade_date: Any, source_url: str) -> list[dict[str, Any]]:
    return _structured_exchange_rows(payload, trade_date=trade_date, exchange="SHFE", source_id="shfe", source_url=source_url)


def parse_ine_daily_payload(payload: Any, trade_date: Any, source_url: str) -> list[dict[str, Any]]:
    return _structured_exchange_rows(payload, trade_date=trade_date, exchange="INE", source_id="ine", source_url=source_url)


def _json_rows(payload: Any, exchange: str) -> list[dict[str, Any]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, f"{exchange} daily payload missing data list")
    return payload["data"]


def parse_dce_daily_payload(payload: Any, trade_date: Any, source_url: str) -> list[dict[str, Any]]:
    out = []
    for raw in _json_rows(payload, "DCE"):
        name = str(raw.get("variety", ""))
        cid = str(raw.get("contractId", "")).strip()
        if not cid or any(x in name for x in ("小计", "总计", "合计")) or cid in {"小计", "总计", "合计"}:
            continue
        out.append(_canonical_row(
            contract_id=cid, variety=_variety(cid), exchange="DCE", trade_date=trade_date,
            open_=raw.get("open"), high=raw.get("high"), low=raw.get("low"), close=raw.get("close"),
            settlement=raw.get("clearPrice"), pre_settlement=raw.get("lastClear"), volume=raw.get("volumn"),
            turnover=raw.get("turnover"), open_interest=raw.get("openInterest"), source_id="dce", source_url=source_url,
            turnover_unit="provider_declared", raw=raw, delivery_month=_delivery_month(cid),
        ))
    return out


def parse_gfex_daily_payload(payload: Any, trade_date: Any, source_url: str) -> list[dict[str, Any]]:
    out = []
    for raw in _json_rows(payload, "GFEX"):
        name = str(raw.get("variety", ""))
        if any(x in name for x in ("小计", "总计", "合计")):
            continue
        code = str(raw.get("varietyOrder") or "").strip().upper()
        month = str(raw.get("delivMonth") or "").strip()
        cid = str(raw.get("contractId") or (code + month)).strip()
        if not cid:
            continue
        out.append(_canonical_row(
            contract_id=cid, variety=code or _variety(cid), exchange="GFEX", trade_date=trade_date,
            open_=raw.get("open"), high=raw.get("high"), low=raw.get("low"), close=raw.get("close"),
            settlement=raw.get("clearPrice"), pre_settlement=raw.get("lastClear"), volume=raw.get("volumn"),
            turnover=raw.get("turnover"), open_interest=raw.get("openInterest"), source_id="gfex", source_url=source_url,
            turnover_unit="provider_declared", raw=raw, delivery_month=month or _delivery_month(cid),
        ))
    return out


def _first(row: dict[str, str], *names: str) -> Optional[str]:
    for name in names:
        if name in row and str(row[name]).strip() != "":
            return row[name]
    return None


def parse_cffex_daily_csv(text: str, trade_date: Any, source_url: str, *, futures_only: bool = False) -> list[dict[str, Any]]:
    if "合约" not in text or "开盘" not in text:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "CFFEX CSV header not recognized")
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
    if not reader.fieldnames:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "CFFEX CSV has no header")
    out = []
    for raw0 in reader:
        raw = {str(k).strip(): (v.strip() if isinstance(v, str) else v) for k, v in raw0.items() if k is not None}
        cid = str(_first(raw, "合约代码", "合约") or "").strip().upper()
        if not cid or any(x in cid for x in ("小计", "总计", "合计")):
            continue
        if futures_only and not re.fullmatch(r"[A-Z]{1,3}\d{4}", cid):
            continue
        out.append(_canonical_row(
            contract_id=cid, variety=_variety(cid), exchange="CFFEX", trade_date=trade_date,
            open_=_first(raw, "今开盘", "开盘价"), high=_first(raw, "最高价"), low=_first(raw, "最低价"), close=_first(raw, "今收盘", "收盘价"),
            settlement=_first(raw, "今结算", "结算价"), pre_settlement=_first(raw, "前结算", "前结算价"), volume=_first(raw, "成交量"),
            turnover=_first(raw, "成交金额", "成交额"), open_interest=_first(raw, "持仓量"), source_id="cffex", source_url=source_url,
            turnover_unit="CNY_10K", raw=raw, delivery_month=_delivery_month(cid),
        ))
    return out


def parse_cffex_history_zip(content: bytes, trade_date: Any, source_url: str, *, futures_only: bool = False) -> list[dict[str, Any]]:
    compact = _compact_date(trade_date)
    target = f"{compact}_1.csv"
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            names = {name.split("/")[-1]: name for name in archive.namelist()}
            if target not in names:
                raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, f"CFFEX archive missing {target}", {"source_url": source_url})
            raw = archive.read(names[target])
    except FinancialDataError:
        raise
    except Exception as exc:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, f"invalid CFFEX history ZIP: {exc}", {"source_url": source_url}) from exc
    text = None
    for encoding in ("gb2312", "gbk", "utf-8-sig"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            pass
    if text is None:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "cannot decode CFFEX CSV")
    return parse_cffex_daily_csv(text, trade_date, source_url, futures_only=futures_only)


def parse_czce_daily_text(text: str, trade_date: Any, source_url: str) -> list[dict[str, Any]]:
    if "您的访问出错了" in text or ("无期" in text and "行情" in text):
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "CZCE returned an error/no-data page", {"source_url": source_url})
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    header_idx = next((i for i, line in enumerate(lines) if "昨结算" in line and "|" in line), None)
    if header_idx is None:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "CZCE daily header not recognized")
    headers = [item.strip() for item in lines[header_idx].split("|")]
    out = []
    for line in lines[header_idx + 1:]:
        if "|" not in line:
            continue
        parts = [item.strip() for item in line.split("|")]
        if len(parts) < len(headers):
            continue
        raw = dict(zip(headers, parts))
        cid = str(_first(raw, "品种月份", "品种代码", "合约代码") or "").strip().upper()
        if not cid or any(x in cid for x in ("小计", "总计", "合计")):
            continue
        out.append(_canonical_row(
            contract_id=cid, variety=_variety(cid), exchange="CZCE", trade_date=trade_date,
            open_=_first(raw, "今开盘", "开盘价"), high=_first(raw, "最高价"), low=_first(raw, "最低价"), close=_first(raw, "今收盘", "收盘价"),
            settlement=_first(raw, "今结算", "结算价"), pre_settlement=_first(raw, "昨结算", "前结算价"), volume=_first(raw, "成交量(手)", "成交量"),
            turnover=_first(raw, "成交额(万元)", "成交额"), open_interest=_first(raw, "空盘量", "持仓量"), source_id="czce", source_url=source_url,
            turnover_unit="CNY_10K" if "成交额(万元)" in raw else "provider_declared", raw=raw, delivery_month=_delivery_month(cid),
        ))
    return out


def _client(client: Optional[HttpClient]) -> HttpClient:
    return client or HttpClient(timeout=15.0, max_retries=2)


def fetch_shfe_daily(trade_date: Any, *, client: Optional[HttpClient] = None) -> list[dict[str, Any]]:
    compact = _compact_date(trade_date)
    url = f"https://www.shfe.com.cn/data/tradedata/future/dailydata/kx{compact}.dat"
    return parse_shfe_daily_payload(_client(client).get_json(url), trade_date, url)


def fetch_ine_daily(trade_date: Any, *, client: Optional[HttpClient] = None) -> list[dict[str, Any]]:
    compact = _compact_date(trade_date)
    url = f"https://www.ine.cn/data/tradedata/future/dailydata/kx{compact}.dat"
    return parse_ine_daily_payload(_client(client).get_json(url), trade_date, url)


def fetch_dce_daily(trade_date: Any, *, client: Optional[HttpClient] = None) -> list[dict[str, Any]]:
    compact = _compact_date(trade_date)
    url = "https://www.dce.com.cn/dcereport/publicweb/dailystat/dayQuotes"
    payload = {"contractId": "", "lang": "zh", "optionSeries": "", "statisticsType": "0", "tradeDate": compact, "tradeType": "1", "varietyId": "all"}
    return parse_dce_daily_payload(_client(client).post_json(url, json=payload), trade_date, url)


def fetch_gfex_daily(trade_date: Any, *, client: Optional[HttpClient] = None) -> list[dict[str, Any]]:
    compact = _compact_date(trade_date)
    url = "https://www.gfex.com.cn/u/interfacesWebTiDayQuotes/loadList"
    headers = {"X-Requested-With": "XMLHttpRequest", "Referer": "https://www.gfex.com.cn/gfex/rihq/hqsj_tjsj.shtml", "User-Agent": "Mozilla/5.0 financial-data/0.2.2"}
    return parse_gfex_daily_payload(_client(client).post_json(url, data={"trade_date": compact, "trade_type": "0"}, headers=headers), trade_date, url)


def fetch_cffex_daily(trade_date: Any, *, client: Optional[HttpClient] = None, futures_only: bool = False) -> list[dict[str, Any]]:
    compact = _compact_date(trade_date)
    month = compact[:6]
    url = f"https://www.cffex.com.cn/sj/historysj/{month}/zip/{month}.zip"
    response = _client(client).get_response(url, headers={"User-Agent": "Mozilla/5.0 financial-data/0.2.2"})
    content = bytes(getattr(response, "content", b""))
    if not content:
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "CFFEX history archive is empty", {"source_url": url})
    return parse_cffex_history_zip(content, trade_date, url, futures_only=futures_only)


def fetch_czce_daily(trade_date: Any, *, client: Optional[HttpClient] = None) -> list[dict[str, Any]]:
    compact = _compact_date(trade_date)
    year = compact[:4]
    if int(year) < 2016:
        raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, "CZCE READY fetcher supports the modern DFSStaticFiles regime from 2016 onward")
    url = f"https://www.czce.com.cn/cn/DFSStaticFiles/Future/{year}/{compact}/FutureDataDaily.txt"
    response = _client(client).get_response(url, headers={"User-Agent": "Mozilla/5.0 financial-data/0.2.2"})
    content = bytes(getattr(response, "content", b""))
    if not content:
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "CZCE daily file is empty", {"source_url": url})
    text = None
    for encoding in ("utf-8-sig", "gb18030", "gbk"):
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            pass
    if text is None:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "cannot decode CZCE daily file", {"source_url": url})
    return parse_czce_daily_text(text, trade_date, url)


_FETCHERS: dict[str, Callable[..., list[dict[str, Any]]]] = {
    "SHFE": fetch_shfe_daily, "INE": fetch_ine_daily, "DCE": fetch_dce_daily,
    "CZCE": fetch_czce_daily, "CFFEX": fetch_cffex_daily, "GFEX": fetch_gfex_daily,
}


def fetch_cn_futures_daily(exchange: str, trade_date: Any, **kwargs: Any) -> list[dict[str, Any]]:
    key = str(exchange).strip().upper()
    if key not in _FETCHERS:
        raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"unsupported China futures exchange: {exchange}")
    return _FETCHERS[key](trade_date, **kwargs)


__all__ = [
    "normalize_trade_date", "validate_futures_daily_row",
    "parse_shfe_daily_payload", "parse_ine_daily_payload", "parse_dce_daily_payload", "parse_gfex_daily_payload",
    "parse_cffex_daily_csv", "parse_cffex_history_zip", "parse_czce_daily_text",
    "fetch_shfe_daily", "fetch_ine_daily", "fetch_dce_daily", "fetch_gfex_daily", "fetch_cffex_daily", "fetch_czce_daily",
    "fetch_cn_futures_daily",
]
