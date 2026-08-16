from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Callable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from ..contracts import DataPoint, DataRequest, ErrorCode, FinancialDataError
from ..instruments import Instrument
from .base import HttpClient


_YAHOO_INTERVALS = {
    "1m": "1m", "2m": "2m", "5m": "5m", "15m": "15m", "30m": "30m", "60m": "60m",
    "1h": "1h", "1d": "1d", "1w": "1wk", "1wk": "1wk", "1mo": "1mo", "3mo": "3mo",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_yahoo_chart_payload(payload, instrument: Instrument, *, retrieved_at: str, interval: str) -> list[DataPoint]:
    chart = payload.get("chart") if isinstance(payload, dict) else None
    if not isinstance(chart, dict):
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "Yahoo chart response missing chart object")
    if chart.get("error"):
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "Yahoo chart returned provider error", {"provider_error": chart.get("error")})
    results = chart.get("result") or []
    if not results:
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "Yahoo chart returned no result", {"symbol": instrument.ticker})

    result = results[0]
    meta = result.get("meta") or {}
    timestamps = result.get("timestamp") or []
    indicators = result.get("indicators") or {}
    quotes = indicators.get("quote") or []
    if not quotes:
        raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "Yahoo chart returned no quote series", {"symbol": instrument.ticker})
    quote = quotes[0]
    adj_sets = indicators.get("adjclose") or []
    adj_close = (adj_sets[0].get("adjclose") or []) if adj_sets else []

    timezone_name = meta.get("exchangeTimezoneName") or meta.get("timezone") or "UTC"
    try:
        exchange_tz = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError):
        exchange_tz = timezone.utc

    arrays = {key: quote.get(key) or [] for key in ("open", "high", "low", "close", "volume")}
    out: list[DataPoint] = []
    for index, timestamp in enumerate(timestamps):
        values = {key: _to_float(array[index]) if index < len(array) else None for key, array in arrays.items()}
        if any(values[key] is None for key in ("open", "high", "low", "close")):
            continue
        dt_utc = datetime.fromtimestamp(int(timestamp), timezone.utc)
        local_dt = dt_utc.astimezone(exchange_tz)
        value = dict(values)
        if index < len(adj_close):
            normalized_adj = _to_float(adj_close[index])
            if normalized_adj is not None:
                value["adj_close"] = normalized_adj
        out.append(DataPoint(
            instrument_id=instrument.canonical_id,
            symbol=instrument.ticker,
            field="bar",
            value=value,
            unit="bar",
            currency=meta.get("currency") or instrument.currency,
            trade_date=local_dt.date().isoformat(),
            as_of=dt_utc.isoformat(),
            retrieved_at=retrieved_at,
            source_id="yahoo",
            source_type="secondary",
            adjustment="none",
            status="verified",
            metadata={
                "provider_symbol": YahooChartAdapter.provider_symbol(instrument),
                "provider_interval": interval,
                "exchange_timezone": timezone_name,
                "exchange_name": meta.get("exchangeName"),
                "source_url": "https://query2.finance.yahoo.com/v8/finance/chart/",
            },
        ))
    if not out:
        raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, "Yahoo chart contained no valid OHLC bars", {"symbol": instrument.ticker})
    return out


class YahooChartAdapter:
    source_id = "yahoo"

    def __init__(self, *, session=None, clock: Callable[[], str] = _now_iso):
        self.client = HttpClient(session=session)
        self.clock = clock

    @staticmethod
    def provider_symbol(instrument: Instrument) -> str:
        if instrument.country == "US":
            return instrument.symbol
        if instrument.country == "HK":
            return instrument.ticker
        raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"Yahoo chart adapter supports US/HK only: {instrument.ticker}")

    def supports(self, request: DataRequest, instrument: Instrument) -> bool:
        return request.field == "kline" and instrument.country in {"US", "HK"}

    def fetch(self, request: DataRequest, instrument: Instrument) -> list[DataPoint]:
        if not self.supports(request, instrument):
            raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"Yahoo chart does not support {request.field} for {instrument.ticker}")
        requested = str(request.params.get("resolution") or request.params.get("interval") or "1d").lower()
        interval = _YAHOO_INTERVALS.get(requested)
        if not interval:
            raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"unsupported Yahoo interval: {requested}", {"interval": requested})

        params: dict[str, object] = {"interval": interval, "events": "div,splits"}
        if request.start or request.end:
            if request.start:
                if len(request.start) <= 10:
                    start_dt = datetime.fromisoformat(request.start).replace(tzinfo=timezone.utc)
                else:
                    start_dt = datetime.fromisoformat(request.start.replace("Z", "+00:00"))
                params["period1"] = int(start_dt.timestamp())
            if request.end:
                if len(request.end) <= 10:
                    end_dt = datetime.fromisoformat(request.end).replace(tzinfo=timezone.utc) + timedelta(days=1)
                else:
                    end_dt = datetime.fromisoformat(request.end.replace("Z", "+00:00"))
                params["period2"] = int(end_dt.timestamp())
        else:
            params["range"] = str(request.params.get("range", "1y"))

        symbol = self.provider_symbol(instrument)
        payload = self.client.get_json(
            f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}",
            params=params,
            headers={"User-Agent": "Mozilla/5.0 financial-data"},
        )
        return parse_yahoo_chart_payload(payload, instrument, retrieved_at=self.clock(), interval=interval)
