---
name: financial-data
description: Use when a task needs real financial-market data retrieval, normalization, source routing, provenance, cross-source validation, fallback, or reproducible derived metrics across A-shares, HK/US equities, rates, macro, futures, options, FX, or crypto.
---

# financial-data

## Purpose
Use this Skill as the shared data layer for financial research, monitoring, reports, and quantitative preparation. It prepares trustworthy data; it does not replace investment analysis or make trading decisions.

Core chain: **Identify → Route → Fetch → Normalize → Validate → Cite → Deliver**.

## Operating contract
1. Resolve the instrument before fetching. Prefer canonical tickers such as `600519.SH`, `0700.HK`, `AAPL.US`; never guess an ambiguous symbol.
2. Route by **market + field + usage**, not by a global favorite website. Read `references/source-routing.md` and the relevant market reference when source choice matters.
3. Every successful datum must retain provenance: `source_id`, `as_of`, `retrieved_at`, field/unit, and applicable currency/period/adjustment metadata. Read `references/data-contract.md`.
4. Percentages are decimals internally; volume units and price-adjustment conventions must be explicit. See `references/market-conventions.md`.
5. Validate before delivery. For supplier-derived or decision-critical data, cross-check an independent source when required. A material disagreement is `SOURCE_CONFLICT`; preserve both observations and explain the likely口径/time difference rather than silently choosing one.
6. Fallback must prefer another domain/rate-limit plane. A failed provider is not equivalent to “no data.” Return a classified error when all routes fail. See `references/fallback-policy.md`.
7. Check `references/compliance.md` before commercial use or redistribution. “Official” does not automatically mean unrestricted use. Never bypass CAPTCHA, access controls, or explicit anti-bot restrictions.
8. Compute deterministic derivatives locally where practical (returns, MA/EMA, RSI, MACD, Bollinger, volatility, drawdown, turnover rate, breadth/concentration). Record algorithm version/parameters when published.
9. Load only the reference needed for the task; do not ingest every market module by default.

## Runtime
Reusable Python lives under `scripts/financial_data/`. Add the Skill `scripts/` directory to `PYTHONPATH`, then:

```python
from financial_data import DataRequest, get_data, result_dict

result = get_data(DataRequest("600519", "quote", require_crosscheck=True))
print(result_dict(result, "compact"))
```

The public call always returns a `DataResult`; unsupported fields, compliance restrictions, stale data, source outages, and conflicts are explicit rather than hidden as empty success.

## Reference routing
- Contract/time/unit semantics: `references/data-contract.md`, `references/market-conventions.md`
- Instrument identity: `references/instrument-master.md`
- Sources/routing/health/fallback: `references/source-registry.md`, `references/source-routing.md`, `references/fallback-policy.md`
- Validation: `references/validation-rules.md`
- Compliance: `references/compliance.md`
- Workflows: `references/workflows.md`
- Markets: `references/a-share.md`, `references/us-hk.md`, `references/macro-rates.md`, `references/futures-commodities.md`, `references/derivatives.md`
