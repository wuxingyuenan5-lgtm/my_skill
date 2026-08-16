# Provider: DCE / 大连商品交易所

last_verified: 2026-08-16

## Identity
Official source of record for DCE contract market statistics, member position rankings, warehouse/delivery and rule parameters.

## Access and authentication
Current reference implementations use public DCE web/report request families without API keys. These are web data services rather than a published versioned API contract; request shapes can change.

## Technical request limits
Official published QPS/RPM/concurrency limit for these public report endpoints: **unknown**. Prefer exchange batch/download endpoints, cache by trading day, avoid per-contract high-concurrency loops and back off on blocking/timeouts.

## Data-range limits
Historical endpoint/layout regimes differ. Current reference daily data uses the official dayQuotes POST family; current positioning reference uses the official batch member-position ZIP family. Validate older backfill regimes separately.

## Freshness and publication timing
Daily statistics/position rankings are post-close datasets; exact availability time is not asserted as an SLA. Downstream jobs should retry conservatively and distinguish no-trading/no-publication from transport failure.

## Licensing and redistribution
Official public data is suitable for research source-of-record use; commercial redistribution and market-data licensing must follow current DCE terms.

## Data-quality limitations
DCE product/contract scope rules and historical ranking formats can differ. Preserve contract ID, variety, trading day, units, and raw file identity.

## Copy guidance
See `../references/futures-ready-core.md` and `../references/futures-positioning-ready-core.md`; reference runtimes `../scripts/financial_data/cn_futures_official.py` and `../scripts/financial_data/futures_positioning.py`. Freeze request JSON/form, ZIP/text parser fixture, date regime and fallback.