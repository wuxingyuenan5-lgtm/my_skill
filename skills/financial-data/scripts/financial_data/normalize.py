from __future__ import annotations

from datetime import datetime
import math
import re
from typing import Any, Optional, Union
from zoneinfo import ZoneInfo


_SUFFIX_MULTIPLIERS = {
    "万": 1e4,
    "亿": 1e8,
    "K": 1e3,
    "M": 1e6,
    "B": 1e9,
    "T": 1e12,
}


def normalize_number(value: Any, *, scale: float = 1.0) -> Optional[Union[float, int]]:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ValueError("boolean is not a numeric market value")
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError("non-finite numeric value")
        out = float(value) * scale
        return int(out) if out.is_integer() else out

    text = str(value).strip().replace(",", "")
    suffix_mult = 1.0
    for suffix, multiplier in _SUFFIX_MULTIPLIERS.items():
        if text.upper().endswith(suffix) if suffix.isascii() else text.endswith(suffix):
            text = text[: -len(suffix)].strip()
            suffix_mult = multiplier
            break
    if not re.fullmatch(r"[-+]?\d+(?:\.\d+)?", text):
        raise ValueError(f"cannot normalize numeric value: {value!r}")
    out = float(text) * suffix_mult * scale
    return int(out) if out.is_integer() else out


def normalize_percentage(value: Any, *, percent_points: bool = False) -> Optional[float]:
    if value is None or value == "":
        return None
    if isinstance(value, str):
        text = value.strip()
        if text.endswith("%"):
            return float(text[:-1].replace(",", "")) / 100.0
        number = normalize_number(text)
        return float(number) / 100.0 if percent_points else float(number)
    number = float(value)
    return number / 100.0 if percent_points else number


def normalize_timestamp(value: Union[str, datetime], *, default_timezone: Optional[str] = None) -> str:
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        if not default_timezone:
            raise ValueError("timezone is required for naive timestamp")
        dt = dt.replace(tzinfo=ZoneInfo(default_timezone))
    return dt.isoformat()


def normalize_currency(currency: Optional[str]) -> Optional[str]:
    if currency is None:
        return None
    code = str(currency).strip().upper()
    aliases = {"RMB": "CNY", "CNH": "CNY", "US$": "USD", "HK$": "HKD"}
    return aliases.get(code, code)
