from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from .source_health import SourceHealthTracker


@dataclass(frozen=True)
class SourceSpec:
    source_id: str
    domains: tuple[str, ...]
    markets: tuple[str, ...]
    fields: tuple[str, ...]
    authority: str
    reliability: str
    freshness: str
    compliance: str
    commercial_use: str
    redistribution: str
    auth: str
    rate_limit: str
    status: str
    last_verified: str
    independence_group: str
    adapter: Optional[str]
    notes: str = ""


class SourceRegistry:
    def __init__(self, sources: Iterable[SourceSpec]):
        self._sources = {s.source_id: s for s in sources}

    def get(self, source_id: str) -> SourceSpec:
        return self._sources[source_id]

    def all(self) -> list[SourceSpec]:
        return list(self._sources.values())

    def candidates(self, market: str, field: str) -> list[SourceSpec]:
        market = market.upper()
        return [
            s
            for s in self._sources.values()
            if (market in s.markets or "GLOBAL" in s.markets)
            and (field in s.fields or "*" in s.fields)
        ]


def default_registry() -> SourceRegistry:
    """Reviewed source catalog for shared runtime routing and project recipes.

    ``last_verified`` records the latest reviewed provider/official-source date;
    it is not automatically rewritten to today's date. Registry presence does
    not imply commercial-use permission or a shared executable adapter.
    """
    return SourceRegistry(
        [
            SourceSpec(
                "tencent", ("qt.gtimg.cn", "web.ifzq.gtimg.cn", "ifzq.gtimg.cn"), ("CN", "HK", "US"),
                ("quote", "price", "turnover", "turnover_rate", "market_cap", "float_market_cap", "pe", "pb", "kline"),
                "B", "A", "A", "C", "research_only", "restricted", "none", "provider_controlled",
                "healthy", "2026-08-15", "tencent", "tencent",
                "Shared adapter supports CN quote/valuation fields and CN K-lines; provider terms require review for commercial use.",
            ),
            SourceSpec(
                "sina", ("hq.sinajs.cn", "quotes.sina.cn", "money.finance.sina.com.cn"), ("CN", "HK", "US"),
                ("quote", "price", "kline", "financial_statements", "fund_flow"),
                "B", "B", "A", "C", "research_only", "restricted", "none", "provider_controlled",
                "healthy", "2026-07-24", "sina", "sina",
                "Independent fallback for selected market data; terms require review.",
            ),
            SourceSpec(
                "eastmoney", ("eastmoney.com", "push2.eastmoney.com", "datacenter-web.eastmoney.com", "searchapi.eastmoney.com"), ("CN", "HK", "US"),
                ("quote", "price", "turnover", "market_cap", "pe", "pb", "fund_flow", "margin", "block_trade", "holder_count", "research", "sector", "limit_state", "market_list", "security_search"),
                "B", "B", "A", "C", "research_only", "restricted", "none", "strict_throttle",
                "healthy", "2026-08-15", "eastmoney", None,
                "Reusable EastmoneyClient exists for datacenter, Push2 market lists and security search; dataset-specific fields remain project recipes.",
            ),
            SourceSpec(
                "cninfo", ("cninfo.com.cn",), ("CN",), ("filings",),
                "A", "B", "A", "B", "verify", "verify", "none", "provider_controlled",
                "healthy", "2026-08-09", "cninfo", None, "Official disclosure platform; usage terms still need task-context review.",
            ),
            SourceSpec(
                "sse_szse", ("sse.com.cn", "szse.cn"), ("CN",), ("filings", "dragon_tiger", "watchlist"),
                "A", "B", "A", "B", "verify", "verify", "none", "provider_controlled",
                "healthy", "2026-08-09", "cn_exchanges", None, "First-party exchange data.",
            ),
            SourceSpec(
                "sec_edgar", ("data.sec.gov", "www.sec.gov"), ("US",),
                ("filings", "fundamentals", "xbrl", "revenue", "net_income", "operating_cash_flow", "assets", "liabilities", "rd_expense", "cross_section_fundamentals", "insider_filings"),
                "A", "A", "A", "A", "allowed", "allowed", "declared_user_agent", "8_per_second",
                "healthy", "2026-07-24", "sec", "sec_edgar", "Official SEC EDGAR data; declared User-Agent required.",
            ),
            SourceSpec(
                "treasury", ("home.treasury.gov",), ("US", "GLOBAL"),
                ("yield_curve", "yield_2y", "yield_10y", "spread_10y_2y"),
                "A", "A", "A", "A", "allowed", "allowed", "none", "reasonable_use",
                "healthy", "2026-07-24", "us_treasury", "treasury", "Official US Treasury yield-curve data.",
            ),
            SourceSpec(
                "cftc", ("publicreporting.cftc.gov",), ("US", "GLOBAL"), ("cot", "positioning"),
                "A", "A", "B", "A", "allowed", "allowed", "none", "reasonable_use",
                "healthy", "2026-07-24", "cftc", None, "Official CFTC public reporting; shared helper is financial_data.cftc.fetch_cot.",
            ),
            SourceSpec(
                "yahoo", ("finance.yahoo.com", "query1.finance.yahoo.com", "query2.finance.yahoo.com"), ("US", "HK", "GLOBAL"),
                ("quote", "price", "kline", "options", "fundamentals", "news"),
                "C", "B", "A", "C", "research_only", "restricted", "mixed_none_or_cookie_crumb", "provider_controlled",
                "healthy", "2026-08-15", "yahoo", "yahoo_chart",
                "Shared adapter supports v8 chart K-lines without crumb; other Yahoo modules may require cookie/crumb and remain recipe-level.",
            ),
            SourceSpec(
                "cboe", ("cdn.cboe.com",), ("US",), ("options", "greeks", "iv", "options_flow"),
                "A", "A", "B", "C", "restricted", "restricted", "none", "provider_controlled",
                "healthy", "2026-07-24", "cboe", None, "Official feed but license/approval requirements apply.",
            ),
            SourceSpec(
                "finra", ("finra.org",), ("US",), ("short_volume",),
                "A", "A", "B", "B", "verify", "restricted", "none", "provider_controlled",
                "healthy", "2026-07-24", "finra", None, "Published data; commercial/scripted-use terms require verification.",
            ),
        ]
    )


__all__ = ["SourceSpec", "SourceRegistry", "SourceHealthTracker", "default_registry"]
