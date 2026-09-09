# HiThink Financial API Recipe Guide

last_verified: 2026-09-08
upstream: <https://github.com/HiThink-Tech/Financial-API>

Use this page only after `providers/hithink-finance.md` has been shortlisted. This is a project-freezing recipe, not a replacement copy of the upstream `hithink-finance` Agent Skill.

## Route selection

Choose one primary path based on the downstream project:

| Need | Preferred path |
|---|---|
| service/backend integration | REST API |
| Agent/IDE with connected service | MCP |
| terminal automation and local data management | CLI |
| notebook/research code | Python SDK |
| broad historical A-share research | market dump → local Parquet/DuckDB |

Do not install every access mode merely because it exists.

## Credentials

Use `HITHINK_FINANCE_API_KEY` or a project secret store. Never freeze a real key into copied recipes, config examples, fixtures, CI logs or Git history.

## Instrument resolution

Do not infer exchange suffixes from a bare ticker. Resolve the user's name/code through the provider symbol-search/meta capability and persist both:

- canonical project instrument identity;
- provider alias (`thscode`).

A provider alias is not the canonical cross-provider instrument ID.

## Small-query REST pattern

For a bounded live query:

1. resolve the instrument;
2. call one dataset-specific endpoint;
3. require business success (`code=0` in the current upstream REST contract);
4. preserve `request_id` when provided;
5. normalize units/dates into the project schema;
6. attach `source_id=hithink_finance`, `retrieved_at` and relevant `as_of`/trade/report dates.

Treat input/auth errors as fixable request errors, not retryable transport failures. Rate limiting (`4001`) and server/network errors may use bounded exponential backoff.

## Large-universe pattern

Do not loop over thousands of stocks if a full-market dump exists.

Preferred A-share history flow:

```text
market-dump endpoint
→ short-lived presigned URL
→ download Parquet immediately
→ verify file/readability
→ persist immutable local copy
→ normalize/query locally
→ incremental refresh from recent-daily dump
```

Never persist the presigned URL as the dataset location because it expires. Persist the downloaded artifact path/checksum and source retrieval metadata instead.

## Current high-value capability groups

### Market data
A-share latest snapshot, historical daily/weekly/monthly data, corporate actions/adjustment factors, trading calendar and symbol metadata.

### Fundamentals and valuation
Income statement, balance sheet, cash-flow statement, financial indicators and latest PE/PB/PS/PCF-style valuation snapshot.

### Auction and microstructure
Call-auction snapshots/benchmark, limit-up/down/break pools, limit-up ladder, anomaly analysis, skyrocket/hot-stock lists and dragon-tiger data.

### Indices and sectors
THS concept/industry/region/special-index catalogs, standard-index/THS-index constituents and index historical/snapshot prices.

### Public funds
Profiles, fund companies/managers, NAV/returns/risk metrics, disclosed stock/bond holdings, industry/asset allocation, holders, dividends, fund financials and ETF/LOF market data.

## Canonical semantics to freeze

At minimum preserve:

- instrument identity separately from `thscode`;
- raw vs adjusted price mode;
- trade date vs publication/report/as-of date;
- currency and amount/volume units;
- provider-derived/editorial labels as a separate data class;
- current-constituent/current-hot-list snapshots separately from historical point-in-time membership;
- null values and data-not-ready states without silent filling.

## Source-of-record policy

HiThink Finance is a structured vendor source. For facts whose legal definition comes from an exchange, issuer filing or regulator disclosure, retain the original official source as the authoritative reference when required.

Examples:

- corporate announcement text → CNINFO/exchange/issuer;
- exchange rule/watchlist definition → exchange;
- normalized financial table for screening → HiThink can be primary structured source, with filing cross-check for material conclusions.

## THS web is a different source family

Do not map all historical `ths` capabilities to `hithink_finance` automatically. Keep public-web/iwencai capabilities separate unless the current Financial-API contract explicitly exposes an equivalent endpoint.

In particular, consensus estimates and semantic iwencai research search remain separate provider capabilities unless upstream adds them.

## Rate-limit policy

The upstream service currently states no cumulative request limit, but uses dynamic throttling and does not commit to a fixed public QPS/RPM value. Therefore freeze:

```text
fixed_qps = provider_not_committed
concurrency = conservative/bounded
429_or_business_4001 = exponential_backoff
bulk_universe = use_batch_or_market_dump
```

Do not invent a hard numerical limit.

## Project smoke tests

For a project that adopts this source, keep tests small and semantic:

- symbol search resolves a known A-share to one expected market identity;
- one historical-price request has monotonic trade dates and plausible OHLC constraints;
- one financial statement returns explicit report periods;
- one market-dump file can be downloaded/read and includes required canonical columns;
- retry classification distinguishes bad parameters/auth from rate-limit/server failure.

## Upstream drift policy

Do not copy the entire upstream API contract into this repository. When a concrete endpoint/field is needed, consult the current upstream capability map/docs, then freeze only the subset the downstream project depends on and record `last_verified`.
