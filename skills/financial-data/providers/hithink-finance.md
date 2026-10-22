# Provider: HiThink Financial API / 同花顺金融数据服务

last_verified: 2026-09-08

## Identity
First-party structured financial-data service published and maintained by HiThink-Tech/同花顺 for AI Agents, quantitative research and application integration. Treat this provider as distinct from THS public-web pages and iwencai: it has a documented API contract, unified authentication and separate operational limits.

It is not an exchange/issuer source of record. For legal filings, exchange rules and issuer disclosures, preserve CNINFO/SSE/SZSE/BSE or the original issuer document as the authoritative fact source when the distinction matters.

Upstream repository: <https://github.com/HiThink-Tech/Financial-API>

## Access and authentication
Remote REST API, MCP, CLI and Python SDK use one API key. Preferred credential name: `HITHINK_FINANCE_API_KEY`.

Do not commit keys to repositories, prompts, logs, examples or generated project files. Downstream projects should read credentials from environment variables or a secret store.

The upstream project also provides a local DuckDB/marketdb workflow and full-market downloadable Parquet data for supported datasets.

## Technical request limits
Official cumulative request cap: **no cumulative limit stated by the provider**.

Published fixed QPS/RPM: **provider_not_committed**. The service uses dynamic rate limiting; avoid bursty high concurrency. Upstream documents rate-limit business code `4001`; lower concurrency and use bounded exponential backoff rather than parallel replay.

For large universes, prefer batch endpoints or market dumps instead of thousands of per-symbol requests.

## Data-range limits
Endpoint-specific rather than one global history rule. The current upstream contract includes single-symbol historical A-share price endpoints plus bulk market-dump products. The bulk path currently advertises roughly 10 years of full-market daily K-line history, a recent 10-trading-day incremental file and full-market adjustment-factor data.

Do not infer minute/tick history from the daily-data product: minute K, tick and Level-2 are outside the current public capability boundary. Exact history/availability for financials, funds, hot lists and specialty datasets should be checked against the current endpoint contract before freezing a downstream assumption.

## Current modeled coverage
The upstream capability map currently documents 59 REST endpoints spanning:

- A-share symbol search/listing and trading calendar;
- latest snapshots and historical daily/weekly/monthly market data;
- corporate actions/adjustment factors;
- income statement, balance sheet, cash-flow statement and financial indicators;
- latest valuation snapshots;
- call-auction snapshots and short-term benchmarks;
- standard indices and THS industry/concept/region/special indices plus constituents;
- limit-up/down/break pools, limit-up ladder, anomalies, hot-stock rankings and dragon-tiger data;
- public-fund profiles, managers, NAV/returns, holdings, allocation, holders, financials and ETF/LOF market data;
- full-market downloadable A-share daily-K and adjustment-factor datasets.

Important current exclusions include minute/tick/Level-2, Hong Kong/US market data, futures/options, macro series, research reports and original news/filing text.

## Bulk-history path
For broad A-share historical research, prefer the market-dump path over per-symbol historical calls. Upstream currently exposes:

- full-market roughly 10-year daily-K Parquet;
- recent 10-trading-day incremental daily-K Parquet;
- full-market adjustment-factor Parquet.

The download endpoints return short-lived presigned URLs, so downstream code should fetch the file promptly and persist its own immutable local copy/checksum. Do not freeze a presigned URL into project configuration.

## Freshness and publication timing
Latest snapshots and intraday specialty datasets are vendor-served near-current data; finality and query availability vary by dataset. Historical backtests must preserve trade date plus the date/time the information became available.

Financial statements and fund holdings are disclosure-period data, not point-in-time values available before publication. Auction, hot-list and anomaly datasets need explicit query-date/as-of semantics.

## Licensing and redistribution
The upstream repository code/documentation is MIT-licensed, but that software license does **not** by itself grant unrestricted redistribution rights to underlying financial data. Treat API account entitlements, provider terms and downstream redistribution/commercial rights separately and verify current terms for production use.

## Data-quality limitations
- Resolve names/tickers to a unique `thscode` before requesting data; do not guess exchange suffixes.
- Preserve null and negative valuation values rather than coercing them.
- Keep THS concepts/themes and vendor anomaly/reason labels classified as vendor-derived/editorial metadata.
- Provider failure, rate limiting or `data not ready` is not equivalent to a legitimate no-data state.
- A-share adjustment mode must be explicit; never mix adjusted prices with raw transaction semantics.
- Historical hot lists, constituents and fund disclosures can introduce look-ahead bias if today's snapshot is applied retrospectively.

## Recommended role inside this Skill
Use HiThink Finance as a **structured A-share/fund provider**, not as the global default for every financial-data task.

Strong fits:

- stable Agent/API access to A-share structured data;
- A-share fundamentals/valuation;
- auction and market-microstructure datasets;
- THS index/concept constituent work;
- public-fund research;
- large historical A-share pulls through Parquet/DuckDB.

Keep THS web/iwencai separate for capabilities such as consensus estimates or semantic research search that are not part of the current Financial-API contract.

## Copy guidance
Primary local recipe: `../references/source-recipes/hithink-finance.md`.

When freezing this source into a downstream project, copy only the needed access path and semantics. Do not vendor the complete upstream Agent Skill or all endpoint documentation. Record:

- upstream repository/version or verification date;
- selected REST/CLI/Python/market-dump route;
- canonical symbol mapping and field map;
- adjustment/timing methodology;
- auth environment-variable name;
- batch/pagination/backoff policy;
- data-rights assumption;
- a small live smoke test or raw fixture.
