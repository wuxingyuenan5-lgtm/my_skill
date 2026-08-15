# financial-data READY Core Expansion Design

## Context

`financial-data` is a handbook-first cross-asset data engineering Skill. The user has approved a hybrid optimization model: keep the broad handbook and copy-ready recipes, while promoting only high-frequency, relatively stable, cross-project integrations into reusable `READY` helpers.

## Goal

Upgrade the most reusable market-data paths without turning the entire handbook into a fragile mega-runtime.

## Approved approach: Hybrid READY + RECIPE

### Promote to READY

1. Tencent A-share K-line helper for daily and supported minute resolutions.
2. Yahoo US/HK chart/K-line helper using the v8 chart endpoint.
3. Eastmoney provider-level reusable HTTP helpers for datacenter and Push2 list/search families.
4. Eastmoney security discovery / market-list helpers that return normalized rows while retaining raw provider fields.

### Keep as RECIPE / RESTRICTED

- A-share margin, block trades, holder count, dividends, lockup, dragon-tiger, limit pools, research, CNINFO/THS endpoints remain primarily recipe-level unless a generic provider helper is sufficient.
- CBOE/FINRA/Nasdaq and licensed/professional sources remain restricted according to their access/compliance status.
- Do not imply commercial permission merely because an endpoint is technically callable.

## Architecture

### Market-data adapters

Keep market-specific adapters small:

- `TencentAdapter`: existing quote fields plus `kline`.
- `YahooChartAdapter`: US/HK `kline` only in this iteration.

K-line points use canonical fields and explicit metadata:

- `field="bar"`
- value: `{open, high, low, close, volume, turnover?}`
- `trade_date`
- `as_of`
- `adjustment`
- provider resolution / provider symbol in metadata

For K-line series, do not force every OHLC field into separate `DataPoint`s. A `bar` object keeps one coherent timestamped observation and is easier for downstream chart/backtest export.

### Eastmoney provider helper

Create `financial_data/eastmoney.py` as a provider-level toolkit rather than one giant facade adapter. It should provide:

- throttled/retrying GET through the existing `HttpClient` boundary;
- `datacenter_query(...)`;
- `push2_list(...)`;
- `market_stock_list(...)`;
- `search_securities(...)` when the public search endpoint response can be normalized;
- explicit business-error detection so `{result: null}` or non-success payloads are not silently treated as “no records.”

The helper returns provider dictionaries, plus normalized convenience output for discovery functions. Dataset-specific recipes can reuse the same client later.

## Source behavior and safety

### Tencent

- Preserve the existing CN symbol resolver and BSE legacy-code guard upstream in Instrument Master.
- Supported minute resolutions are mapped explicitly; unknown resolutions fail closed.
- The provider minute K-line extra field must not be mislabeled as turnover amount. If the source returns turnover-rate-like data, retain it as provider metadata unless confidently normalized.

### Yahoo

- Use the v8 chart endpoint without pretending it is an official licensed production feed.
- Preserve exchange timezone metadata returned by Yahoo where available.
- Reject chart payloads with explicit provider errors.
- Skip null bars rather than constructing invalid OHLC rows.

### Eastmoney

- Serialize/throttle requests at the provider-helper level.
- Classify 403/429/5xx through existing HTTP error handling.
- Detect provider business failures independently of HTTP status.
- Preserve `raw` fields in normalized search/list results for future field-map changes.

## Capability status rules

Only change `RECIPE` -> `READY` when the referenced module/function exists in the repository and is covered by deterministic parser/helper tests.

Expected READY promotions:

- `cn_equity_kline`
- `us_hk_kline`
- `global_equity_search_list` or split market-list/search capability where appropriate
- provider utility entries for Eastmoney generic query helpers

## Testing

Use deterministic local fixtures / fake sessions. No live-provider test is required for correctness claims.

Test cases must cover:

- Tencent daily/minute parsing and resolution mapping;
- Yahoo timestamps, null rows, OHLCV normalization and provider error payload;
- Eastmoney datacenter success, provider-business failure, Push2 market list mapping, and search/list normalization;
- registry/default adapter wiring where applicable;
- capability catalog READY entries point to real code paths.

## Non-goals

- No broad migration of every reference-repo function into the shared facade.
- No credentials or proprietary library/data redistribution.
- No change to `main` or automatic merge of PR #1.
