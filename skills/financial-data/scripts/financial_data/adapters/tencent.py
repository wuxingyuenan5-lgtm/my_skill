from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional
from zoneinfo import ZoneInfo

from ..contracts import DataPoint, DataRequest, ErrorCode, FinancialDataError, QualityFlag
from ..instruments import Instrument
from ..normalize import normalize_percentage
from .base import HttpClient


_TZ_CN = ZoneInfo("Asia/Shanghai")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _prefix(instrument: Instrument) -> str:
    if instrument.ticker.endswith(".SH"):
        return "sh" + instrument.symbol
    if instrument.ticker.endswith(".SZ"):
        return "sz" + instrument.symbol
    if instrument.ticker.endswith(".BJ"):
        return "bj" + instrument.symbol
    raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, "Tencent v0.1.0 adapter supports CN .SH/.SZ/.BJ instruments only")


def _float(vals: list[str], idx: int) -> Optional[float]:
    if idx >= len(vals) or vals[idx] in ("", "-"):
        return None
    try:
        return float(vals[idx])
    except ValueError:
        return None


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
            instrument_id=instrument.canonical_id,
            symbol=instrument.ticker,
            field=field,
            value=value,
            unit=unit,
            currency=currency,
            trade_date=trade_date,
            as_of=as_of,
            retrieved_at=retrieved_at,
            source_id="tencent",
            source_type="secondary",
            status="stale" if stale else "verified",
            quality_flags=list(common_flags),
            metadata={"provider_field": provider_field, "name": name, "source_url": "https://qt.gtimg.cn/"},
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
    _supported = {"quote", "price", "turnover", "turnover_rate", "market_cap", "float_market_cap", "pe", "pe_ttm", "pb"}

    def __init__(self, *, session=None, clock: Callable[[], str] = _now_iso):
        self.client = HttpClient(session=session)
        self.clock = clock

    def supports(self, request: DataRequest, instrument: Instrument) -> bool:
        return instrument.country == "CN" and request.field in self._supported

    def fetch(self, request: DataRequest, instrument: Instrument) -> list[DataPoint]:
        if not self.supports(request, instrument):
            raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"Tencent does not support {request.field} for {instrument.ticker}")
        key = _prefix(instrument)
        text = self.client.get_text(
            f"https://qt.gtimg.cn/q={key}",
            encoding="gbk",
            headers={"User-Agent": "Mozilla/5.0 financial-data/0.1.0"},
        )
        points = parse_tencent_quote_text(text, instrument, retrieved_at=self.clock())
        if request.field == "quote":
            return points
        field = "pe_ttm" if request.field == "pe" else request.field
        return [p for p in points if p.field == field]
