from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Callable, Optional

from ..contracts import DataPoint, DataRequest, ErrorCode, FinancialDataError
from ..instruments import Instrument
from .base import HttpClient


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


_METRIC_TAGS: dict[str, tuple[str, ...]] = {
    "revenue": ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"),
    "net_income": ("NetIncomeLoss", "ProfitLoss"),
    "operating_cash_flow": ("NetCashProvidedByOperatingActivities", "NetCashProvidedByUsedInOperatingActivities"),
    "assets": ("Assets",),
    "liabilities": ("Liabilities",),
    "rd_expense": ("ResearchAndDevelopmentExpense",),
}


class SecEdgarAdapter:
    source_id = "sec_edgar"
    _cik_cache: Optional[dict[str, dict[str, str]]] = None

    def __init__(self, *, session=None, clock: Callable[[], str] = _now_iso):
        self.client = HttpClient(session=session, timeout=10.0, max_retries=2)
        self.clock = clock
        # Cache is per adapter instance for deterministic tests and bounded state.
        self._ticker_map: Optional[dict[str, dict[str, str]]] = None

    def supports(self, request: DataRequest, instrument: Instrument) -> bool:
        return instrument.country == "US" and (request.field in {"filings", "fundamentals", "xbrl"} or request.field in _METRIC_TAGS)

    def _headers(self) -> dict[str, str]:
        contact = os.environ.get("SEC_CONTACT", "").strip()
        if not contact or "@" not in contact:
            raise FinancialDataError(
                ErrorCode.AUTH_REQUIRED,
                "SEC_CONTACT must contain a real contact name/email before SEC network access",
                {"environment_variable": "SEC_CONTACT"},
            )
        return {"User-Agent": f"financial-data/0.1.0 ({contact})", "Accept-Encoding": "gzip, deflate"}

    def _resolve_cik(self, instrument: Instrument) -> tuple[str, Optional[str]]:
        explicit = instrument.external_ids.get("cik") if instrument.external_ids else None
        if explicit:
            return str(explicit).zfill(10), instrument.name
        if self._ticker_map is None:
            payload = self.client.get_json("https://www.sec.gov/files/company_tickers.json", headers=self._headers())
            mapping: dict[str, dict[str, str]] = {}
            for row in payload.values() if isinstance(payload, dict) else []:
                ticker = str(row.get("ticker", "")).upper()
                if ticker:
                    mapping[ticker] = {"cik": str(row.get("cik_str", "")).zfill(10), "company": row.get("title")}
            self._ticker_map = mapping
        row = self._ticker_map.get(instrument.symbol.upper())
        if not row:
            raise FinancialDataError(ErrorCode.INSTRUMENT_NOT_FOUND, f"SEC has no CIK mapping for {instrument.symbol}")
        return row["cik"], row.get("company")

    def fetch(self, request: DataRequest, instrument: Instrument) -> list[DataPoint]:
        if not self.supports(request, instrument):
            raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"SEC EDGAR does not support {request.field} for {instrument.ticker}")
        # Validate contact before even resolving CIK, because mapping itself is an SEC request.
        self._headers()
        cik, company = self._resolve_cik(instrument)
        if request.field == "filings":
            return self._fetch_filings(request, instrument, cik, company)
        return self._fetch_fundamentals(request, instrument, cik, company)

    def _fetch_filings(self, request: DataRequest, instrument: Instrument, cik: str, company: Optional[str]) -> list[DataPoint]:
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        payload = self.client.get_json(url, headers=self._headers())
        recent = ((payload.get("filings") or {}).get("recent") or {})
        forms = recent.get("form") or []
        filing_dates = recent.get("filingDate") or []
        accessions = recent.get("accessionNumber") or []
        docs = recent.get("primaryDocument") or []
        descriptions = recent.get("primaryDocDescription") or []
        form_filter = request.params.get("form")
        limit = int(request.params.get("limit", 50))
        retrieved_at = self.clock()
        out: list[DataPoint] = []
        for i, form in enumerate(forms):
            if form_filter and form != form_filter:
                continue
            filing_date = filing_dates[i] if i < len(filing_dates) else None
            accession = accessions[i] if i < len(accessions) else ""
            doc = docs[i] if i < len(docs) else ""
            accession_compact = accession.replace("-", "")
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_compact}/{doc}" if accession and doc else None
            value = {
                "form": form,
                "accession_number": accession,
                "primary_document": doc,
                "description": descriptions[i] if i < len(descriptions) else "",
                "url": filing_url,
            }
            as_of = f"{filing_date}T00:00:00+00:00" if filing_date else retrieved_at
            out.append(
                DataPoint(
                    instrument_id=instrument.canonical_id,
                    symbol=instrument.ticker,
                    field="filing",
                    value=value,
                    unit="filing",
                    currency=None,
                    publish_date=filing_date,
                    as_of=as_of,
                    retrieved_at=retrieved_at,
                    source_id="sec_edgar",
                    source_type="primary",
                    status="verified",
                    metadata={"company": payload.get("name") or company, "cik": cik, "source_url": url, "as_of_precision": "date"},
                )
            )
            if len(out) >= limit:
                break
        return out

    def _fetch_fundamentals(self, request: DataRequest, instrument: Instrument, cik: str, company: Optional[str]) -> list[DataPoint]:
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        payload = self.client.get_json(url, headers=self._headers())
        gaap = ((payload.get("facts") or {}).get("us-gaap") or {})
        if request.field in _METRIC_TAGS:
            metrics = [request.field]
        else:
            metrics = request.params.get("metrics") or ["revenue", "net_income", "operating_cash_flow", "assets", "liabilities"]
        retrieved_at = self.clock()
        out: list[DataPoint] = []
        for metric in metrics:
            tags = _METRIC_TAGS.get(metric)
            if not tags:
                raise FinancialDataError(ErrorCode.FIELD_NOT_SUPPORTED, f"unsupported SEC standard metric: {metric}")
            tag = next((candidate for candidate in tags if candidate in gaap), None)
            if tag is None:
                continue
            fact = gaap[tag]
            units = fact.get("units") or {}
            unit_key = "USD" if "USD" in units else next(iter(units), None)
            if not unit_key:
                continue
            entries = [e for e in units.get(unit_key, []) if e.get("form") in {"10-Q", "10-K"} and e.get("val") is not None]
            if not entries:
                continue
            # For research/backtest safety, availability is the filing date, not period end.
            latest = max(entries, key=lambda e: (e.get("filed") or "", e.get("end") or "", e.get("start") or ""))
            filed = latest.get("filed")
            end = latest.get("end")
            as_of = f"{filed}T00:00:00+00:00" if filed else retrieved_at
            out.append(
                DataPoint(
                    instrument_id=instrument.canonical_id,
                    symbol=instrument.ticker,
                    field=metric,
                    value=latest.get("val"),
                    unit=unit_key,
                    currency="USD" if unit_key == "USD" else None,
                    report_period=end,
                    publish_date=filed,
                    as_of=as_of,
                    retrieved_at=retrieved_at,
                    source_id="sec_edgar",
                    source_type="primary",
                    status="verified",
                    metadata={
                        "company": payload.get("entityName") or company,
                        "cik": cik,
                        "taxonomy": "us-gaap",
                        "taxonomy_tag": tag,
                        "form": latest.get("form"),
                        "fy": latest.get("fy"),
                        "fp": latest.get("fp"),
                        "source_url": url,
                        "as_of_precision": "date",
                    },
                )
            )
        if not out:
            raise FinancialDataError(ErrorCode.SOURCE_UNAVAILABLE, "SEC companyfacts returned no requested standard metrics", {"ticker": instrument.symbol, "metrics": metrics})
        return out
