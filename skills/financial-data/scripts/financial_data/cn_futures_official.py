from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

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


def _num(value: Any, *, integer: bool = False) -> Optional[float | int]:
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
    *,
    contract_id: str,
    variety: str,
    exchange: str,
    trade_date: Any,
    open_: Any,
    high: Any,
    low: Any,
    close: Any,
    settlement: Any,
    pre_settlement: Any,
    volume: Any,
    turnover: Any,
    open_interest: Any,
    source_id: str,
    source_url: str,
    currency: str = "CNY",
    volume_unit: str = "contracts",
    turnover_unit: str = "provider_declared",
    raw: Optional[dict[str, Any]] = None,
    **extra: Any,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "contract_id": str(contract_id).strip().upper(),
        "variety": str(variety).strip().upper(),
        "exchange": str(exchange).strip().upper(),
        "trade_date": normalize_trade_date(trade_date),
        "open": _num(open_),
        "high": _num(high),
        "low": _num(low),
        "close": _num(close),
        "settlement": _num(settlement),
        "pre_settlement": _num(pre_settlement),
        "volume": _num(volume, integer=True),
        "turnover": _num(turnover),
        "open_interest": _num(open_interest, integer=True),
        "currency": currency,
        "volume_unit": volume_unit,
        "turnover_unit": turnover_unit,
        "source_id": source_id,
        "source_url": source_url,
    }
    if raw is not None:
        row["raw"] = raw
    row.update(extra)
    errors = validate_futures_daily_row(row)
    if errors:
        raise FinancialDataError(
            ErrorCode.VALIDATION_FAILED,
            "invalid futures daily row",
            {"issues": errors, "row": row},
        )
    return row
