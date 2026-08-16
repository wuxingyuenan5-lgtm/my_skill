from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional
from zoneinfo import ZoneInfo

from ..contracts import DataPoint, DataRequest, ErrorCode, FinancialDataError
from ..instruments import Instrument
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
    raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, "Sina v0.1.0 quote adapter supports CN instruments only")


def _num(vals: list[str], idx: int) -> Optional[float]:
    if idx >= len(vals) or vals[idx] == "":
        return None
    try:
        return float(vals[idx])
    except ValueError:
        return None


def parse_sina_quote_text(text: str, instrument: Instrument, *, retrieved_at: str) -> list[DataPoint]:
    if '"' not in text:
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "Sina returned no quote", {"symbol": instrument.ticker})
    vals = text.split('"', 2)[1].split(",")
    if len(vals) < 32 or not vals[0]:
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "Sina quote payload is incomplete", {"symbol": instrument.ticker})
    date = vals[30] if len(vals) > 30 else ""
    clock = vals[31] if len(vals) > 31 else ""
    try:
        dt = datetime.fromisoformat(f"{date}T{clock}").replace(tzinfo=_TZ_CN)
        as_of = dt.isoformat()
        trade_date = date
    except ValueError:
        as_of = retrieved_at
        trade_date = date or None

    name = vals[0]
    fields = {
        "open": (_num(vals, 1), instrument.currency, instrument.currency),
        "previous_close": (_num(vals, 2), instrument.currency, instrument.currency),
        "price": (_num(vals, 3), instrument.currency, instrument.currency),
        "high": (_num(vals, 4), instrument.currency, instrument.currency),
        "low": (_num(vals, 5), instrument.currency, instrument.currency),
        "volume": (_num(vals, 8), "shares", None),
        "turnover": (_num(vals, 9), instrument.currency, instrument.currency),
    }
    out: list[DataPoint] = []
    for field, (value, unit, currency) in fields.items():
        if value is None:
            continue
        out.append(
            DataPoint(
                instrument_id=instrument.canonical_id,
                symbol=instrument.ticker,
                field=field,
                value=value,
                unit=unit,
                currency=currency,
                trade_date=trade_date,
                as_of=as_of,
                retrieved_at=retrieved_at,
                source_id="sina",
                source_type="secondary",
                status="verified",
                metadata={"name": name, "source_url": "https://hq.sinajs.cn/"},
            )
        )
    return out


class SinaAdapter:
    source_id = "sina"
    _supported = {"quote", "price"}

    def __init__(self, *, session=None, clock: Callable[[], str] = _now_iso):
        self.client = HttpClient(session=session)
        self.clock = clock

    def supports(self, request: DataRequest, instrument: Instrument) -> bool:
        return instrument.country == "CN" and request.field in self._supported

    def fetch(self, request: DataRequest, instrument: Instrument) -> list[DataPoint]:
        if not self.supports(request, instrument):
            raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"Sina does not support {request.field} for {instrument.ticker}")
        key = _prefix(instrument)
        text = self.client.get_text(
            f"https://hq.sinajs.cn/list={key}",
            encoding="gbk",
            headers={"Referer": "https://finance.sina.com.cn/", "User-Agent": "Mozilla/5.0 financial-data/0.1.0"},
        )
        points = parse_sina_quote_text(text, instrument, retrieved_at=self.clock())
        if request.field == "quote":
            return points
        return [p for p in points if p.field == request.field]
