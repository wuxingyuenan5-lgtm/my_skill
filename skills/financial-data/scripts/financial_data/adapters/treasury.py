from __future__ import annotations

import csv
from datetime import datetime, timezone
import io
from typing import Callable

from ..contracts import DataPoint, DataRequest, ErrorCode, FinancialDataError, QualityFlag
from ..instruments import Instrument
from ..normalize import normalize_percentage
from .base import HttpClient


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


_COLUMNS = {
    "1 Mo": "yield_1m",
    "3 Mo": "yield_3m",
    "6 Mo": "yield_6m",
    "1 Yr": "yield_1y",
    "2 Yr": "yield_2y",
    "5 Yr": "yield_5y",
    "10 Yr": "yield_10y",
    "20 Yr": "yield_20y",
    "30 Yr": "yield_30y",
}


class TreasuryAdapter:
    source_id = "treasury"
    _supported = {"yield_curve", "yield_2y", "yield_10y", "spread_10y_2y"}

    def __init__(self, *, session=None, clock: Callable[[], str] = _now_iso):
        self.client = HttpClient(session=session, timeout=10.0)
        self.clock = clock

    def supports(self, request: DataRequest, instrument: Instrument) -> bool:
        return request.field in self._supported

    def fetch(self, request: DataRequest, instrument: Instrument) -> list[DataPoint]:
        if not self.supports(request, instrument):
            raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"Treasury does not support {request.field}")
        now = datetime.fromisoformat(self.clock().replace("Z", "+00:00"))
        year = int(request.params.get("year", now.year))
        url = (
            "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
            f"daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve"
            f"&field_tdr_date_value={year}&page&_format=csv"
        )
        text = self.client.get_text(url, headers={"User-Agent": "financial-data/0.1.0"})
        rows = list(csv.DictReader(io.StringIO(text)))
        if not rows:
            raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "Treasury yield curve returned no rows", {"year": year})
        try:
            latest = max(rows, key=lambda r: datetime.strptime(r["Date"], "%m/%d/%Y"))
            trade_date = datetime.strptime(latest["Date"], "%m/%d/%Y").date().isoformat()
        except Exception as exc:
            raise FinancialDataError(ErrorCode.NORMALIZATION_ERROR, f"cannot parse Treasury date: {exc}") from exc

        retrieved_at = self.clock()
        as_of = f"{trade_date}T00:00:00+00:00"
        points: list[DataPoint] = []
        for column, field in _COLUMNS.items():
            raw = (latest.get(column) or "").strip()
            if not raw:
                continue
            try:
                value = normalize_percentage(float(raw), percent_points=True)
            except ValueError:
                continue
            points.append(
                DataPoint(
                    instrument_id=instrument.canonical_id,
                    symbol=instrument.ticker,
                    field=field,
                    value=value,
                    unit="ratio",
                    currency=None,
                    trade_date=trade_date,
                    as_of=as_of,
                    retrieved_at=retrieved_at,
                    source_id="treasury",
                    source_type="primary",
                    status="verified",
                    metadata={"maturity": column, "source_url": url, "as_of_precision": "date"},
                )
            )
        by_field = {p.field: p for p in points}
        if "yield_10y" in by_field and "yield_2y" in by_field:
            points.append(
                DataPoint(
                    instrument_id=instrument.canonical_id,
                    symbol=instrument.ticker,
                    field="spread_10y_2y",
                    value=by_field["yield_10y"].value - by_field["yield_2y"].value,
                    unit="ratio",
                    currency=None,
                    trade_date=trade_date,
                    as_of=as_of,
                    retrieved_at=retrieved_at,
                    source_id="treasury",
                    source_type="derived",
                    status="verified",
                    derived_from=["yield_10y", "yield_2y"],
                    algorithm_version="financial-data/0.1.0:10y_minus_2y",
                    metadata={"source_url": url, "as_of_precision": "date"},
                )
            )
        else:
            for p in points:
                p.quality_flags.append(QualityFlag.PARTIAL_DATA.value)

        if request.field == "yield_curve":
            return points
        return [p for p in points if p.field == request.field]
