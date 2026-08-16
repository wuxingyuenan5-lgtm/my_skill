from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any, Iterable, Mapping

_RESOLUTION_ALIASES = {"1M":"1M","M":"1M","1MON":"1M","1MONTH":"1M","1W":"1W","W":"1W","1D":"1D","D":"1D","1H":"60","H":"60","2H":"120","4H":"240"}


def normalize_resolution(value: Any) -> str:
    """Normalize common project timeframe labels to TradingView ResolutionString."""
    raw = str(value).strip()
    upper = raw.upper()
    if upper in _RESOLUTION_ALIASES:
        return _RESOLUTION_ALIASES[upper]
    if upper.endswith("MIN") and upper[:-3].isdigit():
        return upper[:-3]
    if upper.endswith("M") and upper[:-1].isdigit():
        return upper[:-1]
    if upper.endswith("H") and upper[:-1].isdigit():
        return str(int(upper[:-1]) * 60)
    if raw.isdigit():
        return raw
    raise ValueError(f"Unsupported resolution: {value!r}")


def _parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        dt = datetime.combine(value, time.min)
    elif isinstance(value, (int, float)):
        number = float(value)
        if abs(number) >= 10_000_000_000:
            number /= 1000.0
        dt = datetime.fromtimestamp(number, tz=timezone.utc)
    elif isinstance(value, str):
        text = value.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            dt = datetime.combine(date.fromisoformat(text), time.min)
    else:
        raise TypeError(f"Unsupported time value: {type(value)!r}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _daily_datetime(row: Mapping[str, Any]) -> datetime:
    value = row.get("trade_date") or row.get("date") or row.get("timestamp") or row.get("time")
    if value is None:
        raise KeyError("daily bar requires trade_date/date/timestamp/time")
    if isinstance(value, datetime):
        d = value.date()
    elif isinstance(value, date):
        d = value
    elif isinstance(value, (int, float)):
        d = _parse_datetime(value).date()
    else:
        text = str(value).strip()
        if "T" in text or " " in text:
            d = _parse_datetime(text).date()
        else:
            d = date.fromisoformat(text[:10])
    return datetime.combine(d, time.min, tzinfo=timezone.utc)


def _intraday_datetime(row: Mapping[str, Any]) -> datetime:
    value = row.get("timestamp")
    if value is None:
        value = row.get("time")
    if value is None:
        raise KeyError("intraday bar requires timestamp/time")
    return _parse_datetime(value)


def _numeric(row: Mapping[str, Any], key: str, *, optional: bool = False):
    value = row.get(key)
    if value is None:
        if optional:
            return None
        raise KeyError(f"bar requires {key}")
    return float(value)


def to_tradingview_bar(row: Mapping[str, Any], *, daily: bool = False) -> dict[str, Any]:
    """Convert canonical OHLCV to Advanced Charts Bar (UTC milliseconds)."""
    dt = _daily_datetime(row) if daily else _intraday_datetime(row)
    out = {"time": int(dt.timestamp()*1000), "open": _numeric(row,"open"), "high": _numeric(row,"high"), "low": _numeric(row,"low"), "close": _numeric(row,"close")}
    volume = _numeric(row,"volume",optional=True)
    if volume is not None:
        out["volume"] = volume
    return out


def to_lightweight_bar(row: Mapping[str, Any], *, daily: bool = False) -> dict[str, Any]:
    """Convert canonical OHLCV to Lightweight Charts candlestick data."""
    chart_time: Any = _daily_datetime(row).date().isoformat() if daily else int(_intraday_datetime(row).timestamp())
    return {"time": chart_time, "open": _numeric(row,"open"), "high": _numeric(row,"high"), "low": _numeric(row,"low"), "close": _numeric(row,"close")}


def to_udf_history(rows: Iterable[Mapping[str, Any]], *, daily: bool = False) -> dict[str, Any]:
    """Convert canonical bars to TradingView UDF `/history` response (Unix seconds)."""
    normalized = []
    for row in rows:
        dt = _daily_datetime(row) if daily else _intraday_datetime(row)
        normalized.append((int(dt.timestamp()), row))
    if not normalized:
        return {"s": "no_data"}
    normalized.sort(key=lambda x: x[0])
    out = {"s":"ok","t":[t for t,_ in normalized],"o":[_numeric(r,"open") for _,r in normalized],"h":[_numeric(r,"high") for _,r in normalized],"l":[_numeric(r,"low") for _,r in normalized],"c":[_numeric(r,"close") for _,r in normalized]}
    volumes = [_numeric(r,"volume",optional=True) for _,r in normalized]
    if all(v is not None for v in volumes):
        out["v"] = volumes
    return out
