from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional
from zoneinfo import ZoneInfo

from ..contracts import DataPoint, DataRequest, ErrorCode, FinancialDataError, QualityFlag
from ..instruments import Instrument
from ..normalize import normalize_percentage
from .base import HttpClient


_TZ_CN = ZoneInfo("Asia/Shanghai")
_KLINE_RESOLUTIONS = {
    "1m": "m1", "5m": "m5", "15m": "m15", "30m": "m30", "60m": "m60", "1h": "m60",
    "1d": "day", "d": "day", "day": "day", "1w": "week", "w": "week", "week": "week",
    "1mo": "month", "month": "month",
}
_MINUTE_RESOLUTIONS = {"m1", "m5", "m15", "m30", "m60"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _prefix(instrument: Instrument) -> str:
    if instrument.ticker.endswith(".SH"):
        return "sh" + instrument.symbol
    if instrument.ticker.endswith(".SZ"):
        return "sz" + instrument.symbol
    if instrument.ticker.endswith(".BJ"):
        return "bj" + instrument.symbol
    raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, "Tencent adapter supports CN .SH/.SZ/.BJ instruments only")


def _float(vals: list[str], idx: int) -> Optional[float]:
    if idx >= len(vals) or vals[idx] in ("", "-"):
        return None
    try:
        return float(vals[idx])
    except ValueError:
        return None


def _number(value) -> Optional[float]:
    if value in (None, "", "-"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _bar_time(token, provider_resolution: str) -> tuple[str, str]:
    text = str(token)
    if provider_resolution in _MINUTE_RESOLUTIONS:
        for fmt in ("%Y%m%d%H%M", "%Y-%m-%d %H:%M", "%Y%m%d%H%M%S"):
            try:
                dt = datetime.strptime(text, fmt).replace(tzinfo=_TZ_CN)
                return dt.isoformat(), dt.date().isoformat()
            except ValueError:
                continue
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "Tencent returned an unrecognized intraday bar timestamp", {"timestamp": text})
    try:
        dt = datetime.strptime(text[:10], "%Y-%m-%d").replace(tzinfo=_TZ_CN)
    except ValueError as exc:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "Tencent returned an unrecognized daily bar date", {"date": text}) from exc
    return dt.isoformat(), dt.date().isoformat()


def parse_tencent_kline_payload(payload, instrument: Instrument, *, resolution: str, retrieved_at: str, adjustment: str = "qfq") -> list[DataPoint]:
    provider_resolution = _KLINE_RESOLUTIONS.get(str(resolution).lower())
    if not provider_resolution:
        raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"unsupported Tencent K-line resolution: {resolution}", {"resolution": resolution})
    code = payload.get("code", 0) if isinstance(payload, dict) else None
    if code not in (0, "0", None):
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "Tencent K-line endpoint returned provider error", {"code": code, "msg": payload.get("msg") if isinstance(payload, dict) else None})

    key = _prefix(instrument)
    node = ((payload.get("data") or {}).get(key) or {}) if isinstance(payload, dict) else {}
    if provider_resolution in _MINUTE_RESOLUTIONS:
        series = node.get(provider_resolution)
        normalized_adjustment = "none"
    else:
        adj = str(adjustment or "none").lower()
        if adj not in {"qfq", "hfq", "none"}:
            raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"unsupported Tencent adjustment: {adjustment}", {"adjustment": adjustment})
        candidates = [] if adj == "none" else [f"{adj}{provider_resolution}"]
        candidates.append(provider_resolution)
        series = next((node.get(name) for name in candidates if node.get(name) is not None), None)
        normalized_adjustment = adj

    if not isinstance(series, list) or not series:
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "Tencent returned no K-line rows", {"symbol": instrument.ticker, "resolution": resolution})

    out: list[DataPoint] = []
    for row in series:
        if not isinstance(row, (list, tuple)) or len(row) < 6:
            continue
        open_, close, high, low, volume = (_number(row[i]) for i in range(1, 6))
        if any(value is None for value in (open_, close, high, low)):
            continue
        as_of, trade_date = _bar_time(row[0], provider_resolution)
        out.append(DataPoint(
            instrument_id=instrument.canonical_id,
            symbol=instrument.ticker,
            field="bar",
            value={"open": open_, "high": high, "low": low, "close": close, "volume": volume},
            unit="bar",
            currency=instrument.currency,
            trade_date=trade_date,
            as_of=as_of,
            retrieved_at=retrieved_at,
            source_id="tencent",
            source_type="secondary",
            adjustment=normalized_adjustment,
            status="verified",
            metadata={
                "provider_symbol": key,
                "provider_resolution": provider_resolution,
                "provider_extra_fields": [str(value) for value in row[6:]],
                "volume_unit": "provider_native",
                "source_url": "https://web.ifzq.gtimg.cn/",
            },
        ))
    if not out:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "Tencent K-line rows contained no valid OHLC bars", {"symbol": instrument.ticker, "resolution": resolution})
    return out


def parse_tencent_quote_text(text: str, instrument: Instrument, *, retrieved_at: str) -> list[DataPoint]:
    vals: Optional[list[str]] = None
    for line in text.strip().split(";"):
        if '"' not in line or "=" not in line:
            continue
        candidate = line.split('"', 2)[1].split("~")
        if len(candidate) >= 53 and candidate[2] == instrument.symbol:
            vals = candidate
            break
    if vals is None:
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "Tencent returned no matching quote", {"symbol": instrument.ticker})

    provider_ts = vals[30] if len(vals) > 30 else ""
    if provider_ts and len(provider_ts) >= 14 and provider_ts[:14].isdigit():
        dt = datetime.strptime(provider_ts[:14], "%Y%m%d%H%M%S").replace(tzinfo=_TZ_CN)
        as_of = dt.isoformat()
        trade_date = dt.date().isoformat()
    else:
        as_of = retrieved_at
        trade_date = None

    price = _float(vals, 3)
    previous_close = _float(vals, 4)
    turnover_wan = _float(vals, 37)
    stale = bool(price and previous_close and turnover_wan == 0 and price == previous_close)
    common_flags = [QualityFlag.STALE_DATA.value] if stale else []
    name = vals[1] if len(vals) > 1 else None

    def point(field: str, value, unit: str, *, currency: Optional[str] = None, provider_field: Optional[str] = None) -> Optional[DataPoint]:
        if value is None:
            return None
        return DataPoint(
            instrument_id=instrument.canonical_id, symbol=instrument.ticker, field=field, value=value, unit=unit,
            currency=currency, trade_date=trade_date, as_of=as_of, retrieved_at=retrieved_at,
            source_id="tencent", source_type="secondary", status="stale" if stale else "verified",
            quality_flags=list(common_flags), metadata={"provider_field": provider_field, "name": name, "source_url": "https://qt.gtimg.cn/"},
        )

    raw = [
        point("price", price, instrument.currency, currency=instrument.currency, provider_field="3"),
        point("previous_close", previous_close, instrument.currency, currency=instrument.currency, provider_field="4"),
        point("open", _float(vals, 5), instrument.currency, currency=instrument.currency, provider_field="5"),
        point("change", _float(vals, 31), instrument.currency, currency=instrument.currency, provider_field="31"),
        point("change_pct", normalize_percentage(_float(vals, 32), percent_points=True), "ratio", provider_field="32"),
        point("high", _float(vals, 33), instrument.currency, currency=instrument.currency, provider_field="33"),
        point("low", _float(vals, 34), instrument.currency, currency=instrument.currency, provider_field="34"),
        point("turnover", None if turnover_wan is None else turnover_wan * 10_000, instrument.currency, currency=instrument.currency, provider_field="37_wan"),
        point("turnover_rate", normalize_percentage(_float(vals, 38), percent_points=True), "ratio", provider_field="38"),
        point("pe_ttm", _float(vals, 39), "x", provider_field="39"),
        point("amplitude", normalize_percentage(_float(vals, 43), percent_points=True), "ratio", provider_field="43"),
        point("float_market_cap", None if _float(vals, 44) is None else _float(vals, 44) * 1e8, instrument.currency, currency=instrument.currency, provider_field="44_yi"),
        point("market_cap", None if _float(vals, 45) is None else _float(vals, 45) * 1e8, instrument.currency, currency=instrument.currency, provider_field="45_yi"),
        point("pb", _float(vals, 46), "x", provider_field="46"),
        point("limit_up", _float(vals, 47), instrument.currency, currency=instrument.currency, provider_field="47"),
        point("limit_down", _float(vals, 48), instrument.currency, currency=instrument.currency, provider_field="48"),
        point("volume_ratio", _float(vals, 49), "x", provider_field="49"),
        point("pe_static", _float(vals, 52), "x", provider_field="52"),
    ]
    return [p for p in raw if p is not None]


class TencentAdapter:
    source_id = "tencent"
    _supported = {"quote", "price", "turnover", "turnover_rate", "market_cap", "float_market_cap", "pe", "pe_ttm", "pb", "kline"}

    def __init__(self, *, session=None, clock: Callable[[], str] = _now_iso):
        self.client = HttpClient(session=session)
        self.clock = clock

    def supports(self, request: DataRequest, instrument: Instrument) -> bool:
        return instrument.country == "CN" and request.field in self._supported

    def _kline_request(self, request: DataRequest, instrument: Instrument) -> tuple[str, dict[str, str], str, str]:
        resolution = str(request.params.get("resolution") or request.params.get("interval") or "1d").lower()
        provider_resolution = _KLINE_RESOLUTIONS.get(resolution)
        if not provider_resolution:
            raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"unsupported Tencent K-line resolution: {resolution}", {"resolution": resolution})
        key = _prefix(instrument)
        count = int(request.params.get("count", 320))
        if provider_resolution in _MINUTE_RESOLUTIONS:
            adjustment = "none"
            url = "https://ifzq.gtimg.cn/appstock/app/kline/mkline"
            params = {"param": f"{key},{provider_resolution},,{count}"}
        else:
            adjustment = str(request.params.get("adjustment", "qfq")).lower()
            if adjustment not in {"qfq", "hfq", "none"}:
                raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"unsupported Tencent adjustment: {adjustment}", {"adjustment": adjustment})
            start, end = request.start or "", request.end or ""
            url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
            params = {"param": f"{key},{provider_resolution},{start},{end},{count},{adjustment}"}
        return url, params, resolution, adjustment

    def fetch(self, request: DataRequest, instrument: Instrument) -> list[DataPoint]:
        if not self.supports(request, instrument):
            raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"Tencent does not support {request.field} for {instrument.ticker}")
        if request.field == "kline":
            url, params, resolution, adjustment = self._kline_request(request, instrument)
            payload = self.client.get_json(url, params=params, headers={"User-Agent": "Mozilla/5.0 financial-data"})
            return parse_tencent_kline_payload(payload, instrument, resolution=resolution, retrieved_at=self.clock(), adjustment=adjustment)

        key = _prefix(instrument)
        text = self.client.get_text(f"https://qt.gtimg.cn/q={key}", encoding="gbk", headers={"User-Agent": "Mozilla/5.0 financial-data/0.1.0"})
        points = parse_tencent_quote_text(text, instrument, retrieved_at=self.clock())
        if request.field == "quote":
            return points
        field = "pe_ttm" if request.field == "pe" else request.field
        return [p for p in points if p.field == field]
