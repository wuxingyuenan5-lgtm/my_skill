from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Optional

from .contracts import ErrorCode, FinancialDataError


# Explicit exchange-traded index aliases/codes we support without ambiguity in v0.1.0.
_CN_INDEXES = {
    "000001": ("SSE", "SH", "上证指数"),
    "000016": ("SSE", "SH", "上证50"),
    "000300": ("SSE", "SH", "沪深300"),
    "000688": ("SSE", "SH", "科创50"),
    "000852": ("SSE", "SH", "中证1000"),
    "000905": ("SSE", "SH", "中证500"),
    "399001": ("SZSE", "SZ", "深证成指"),
    "399006": ("SZSE", "SZ", "创业板指"),
}

_BARE_CN_INDEXES = {k: v for k, v in _CN_INDEXES.items() if k != "000001"}


_RATE_ALIASES = {
    "UST2Y": ("UST2Y.US", "US Treasury 2Y"),
    "UST10Y": ("UST10Y.US", "US Treasury 10Y"),
    "UST30Y": ("UST30Y.US", "US Treasury 30Y"),
    "USTCURVE": ("USTCURVE.US", "US Treasury Yield Curve"),
}

_INDEX_ALIASES = {
    "SPX": ("SPX.US", "index", "US", "USD", "CBOE", "S&P 500"),
    "NDX": ("NDX.US", "index", "US", "USD", "NASDAQ", "NASDAQ 100"),
    "DJI": ("DJI.US", "index", "US", "USD", "DJI", "Dow Jones Industrial Average"),
    "HSI": ("HSI.HK", "index", "HK", "HKD", "HKEX", "Hang Seng Index"),
}


@dataclass(frozen=True)
class Instrument:
    canonical_id: str
    symbol: str
    exchange: str
    ticker: str
    name: Optional[str]
    asset_class: str
    currency: str
    country: str
    aliases: tuple[str, ...] = field(default_factory=tuple)
    external_ids: dict[str, str] = field(default_factory=dict)


def _canonical_id(asset_class: str, country: str, ticker: str) -> str:
    token = ticker.replace(".", "_").replace("-", "_")
    return f"{asset_class}_{country.lower()}_{token}"


def normalize_symbol(query: str, market: Optional[str] = None) -> str:
    return InstrumentMaster().resolve(query, market=market).ticker


class InstrumentMaster:
    """Deterministic symbol resolver for common CN/HK/US instruments.

    v0.1.0 intentionally does not fuzzy-search company names. Ambiguity is surfaced
    instead of guessed.
    """

    def resolve(self, query: str, market: Optional[str] = None) -> Instrument:
        if not isinstance(query, str) or not query.strip():
            raise FinancialDataError(ErrorCode.INSTRUMENT_NOT_FOUND, "instrument is empty")

        raw = query.strip()
        upper = raw.upper()
        market_upper = market.upper() if market else None

        if upper in _RATE_ALIASES:
            ticker, name = _RATE_ALIASES[upper]
            return Instrument(
                canonical_id=_canonical_id("rates", "US", ticker),
                symbol=upper, exchange="USTREASURY", ticker=ticker, name=name,
                asset_class="rates", currency="USD", country="US", aliases=(upper,),
            )

        if upper in _INDEX_ALIASES:
            ticker, asset_class, country, currency, exchange, name = _INDEX_ALIASES[upper]
            return Instrument(
                canonical_id=_canonical_id(asset_class, country, ticker),
                symbol=ticker.split(".")[0],
                exchange=exchange,
                ticker=ticker,
                name=name,
                asset_class=asset_class,
                currency=currency,
                country=country,
                aliases=(upper,),
            )

        # Explicit suffixes take precedence.
        for suffix, exchange, country, currency in (
            (".SH", "SSE", "CN", "CNY"),
            (".SZ", "SZSE", "CN", "CNY"),
            (".BJ", "BSE", "CN", "CNY"),
            (".HK", "HKEX", "HK", "HKD"),
            (".US", "US", "US", "USD"),
        ):
            if upper.endswith(suffix):
                base = upper[: -len(suffix)]
                if suffix == ".HK":
                    if not base.isdigit() or len(base) > 5:
                        self._fail(raw, "invalid Hong Kong ticker")
                    base = base.zfill(4)
                elif suffix in {".SH", ".SZ", ".BJ"}:
                    if not (base.isdigit() and len(base) == 6):
                        self._fail(raw, "China ticker must be six digits")
                elif suffix == ".US":
                    if not re.fullmatch(r"[A-Z][A-Z0-9.-]{0,9}", base):
                        self._fail(raw, "invalid US ticker")
                ticker = f"{base}{suffix}"
                asset_class = "index" if base in _CN_INDEXES and suffix in {".SH", ".SZ"} else "equity"
                return Instrument(
                    canonical_id=_canonical_id(asset_class, country, ticker),
                    symbol=base,
                    exchange=exchange,
                    ticker=ticker,
                    name=_CN_INDEXES.get(base, (None, None, None))[2] if asset_class == "index" else None,
                    asset_class=asset_class,
                    currency=currency,
                    country=country,
                )

        # Market override can disambiguate numeric inputs.
        if market_upper in {"HK", "HKG"} and upper.isdigit():
            base = upper.zfill(4)
            ticker = f"{base}.HK"
            return Instrument(_canonical_id("equity", "HK", ticker), base, "HKEX", ticker, None, "equity", "HKD", "HK")
        if market_upper in {"US", "USA"} and re.fullmatch(r"[A-Z][A-Z0-9.-]{0,9}", upper):
            ticker = f"{upper}.US"
            return Instrument(_canonical_id("equity", "US", ticker), upper, "US", ticker, None, "equity", "USD", "US")

        if upper.isdigit() and len(upper) == 6:
            if upper in _BARE_CN_INDEXES:
                exchange, suffix, name = _BARE_CN_INDEXES[upper]
                ticker = f"{upper}.{suffix}"
                return Instrument(_canonical_id("index", "CN", ticker), upper, exchange, ticker, name, "index", "CNY", "CN")
            if upper.startswith("920"):
                ticker = f"{upper}.BJ"
                return Instrument(_canonical_id("equity", "CN", ticker), upper, "BSE", ticker, None, "equity", "CNY", "CN")
            # Most legacy BSE 43/83/87/88 series migrated to 920xxx in 2026.
            # Do not silently map because the suffix is not a guaranteed one-to-one rule.
            if upper.startswith(("43", "83", "87", "88")):
                raise FinancialDataError(
                    ErrorCode.INSTRUMENT_NOT_FOUND,
                    f"{raw} looks like a legacy BSE code; resolve the current 920xxx code before requesting market data",
                    {"input": raw, "reason": "legacy_bse_code"},
                )
            if upper.startswith(("5", "6", "9")):
                suffix, exchange = "SH", "SSE"
            elif upper.startswith(("0", "1", "2", "3")):
                suffix, exchange = "SZ", "SZSE"
            elif upper.startswith(("4", "8")):
                # Remaining bare legacy-style BSE codes are treated as ambiguous.
                raise FinancialDataError(
                    ErrorCode.INSTRUMENT_NOT_FOUND,
                    f"{raw} is ambiguous under current BSE code migration; pass an explicit current .BJ ticker",
                    {"input": raw, "reason": "ambiguous_bse_code"},
                )
            else:
                self._fail(raw, "unrecognized China ticker prefix")
            ticker = f"{upper}.{suffix}"
            return Instrument(_canonical_id("equity", "CN", ticker), upper, exchange, ticker, None, "equity", "CNY", "CN")

        # Bare HK tickers are intentionally not guessed because short numeric strings can
        # collide with non-HK identifiers. Require `.HK` or market="HK".

        if re.fullmatch(r"[A-Z][A-Z0-9.-]{0,9}", upper):
            ticker = f"{upper}.US"
            return Instrument(_canonical_id("equity", "US", ticker), upper, "US", ticker, None, "equity", "USD", "US")

        self._fail(raw, "unsupported or ambiguous instrument; use a canonical ticker such as 600519.SH, 0700.HK, or AAPL.US")

    @staticmethod
    def _fail(query: str, reason: str) -> None:
        raise FinancialDataError(ErrorCode.INSTRUMENT_NOT_FOUND, f"{query}: {reason}", {"input": query})
