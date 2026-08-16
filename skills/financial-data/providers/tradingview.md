# Provider / integration: TradingView

last_verified: 2026-08-16
official_reference: https://www.tradingview.com/charting-library-docs/latest/connecting_data/

## Identity
Primarily a charting/integration ecosystem in this Skill, not a generic data-extraction provider. Widgets can display TradingView-supplied symbols; Advanced Charts/Trading Platform are libraries integrated with a project datafeed; Lightweight Charts renders project data; Pine runs inside TradingView's scripting environment.

## Access and authentication
Advanced Charts repository/library access is permission-controlled. TradingView documentation explicitly states Advanced Charts/Trading Platform **do not contain market data**: the integrator supplies its own or third-party data through Datafeed/UDF. Widget/Pine access follows TradingView product/account terms.

## Technical request limits
There is no universal “TradingView market-data API QPS” applicable to a project-owned Datafeed: its limits come from the project's own backend/provider. Do not scrape TradingView pages as a substitute for a licensed/source API. Widget/library limits and licensing are product-specific.

## Data-range limits
Advanced Charts can request whatever history the project's datafeed can supply, subject to library callbacks/configuration and the upstream provider. It is not a source of arbitrary downloadable TradingView history.

## Freshness and publication timing
For own-data charts, freshness is determined by the upstream backend and `subscribeBars`/quote implementation. Widgets/Pine reflect TradingView's supported symbol/feed arrangements.

## Licensing and redistribution
Advanced Charts is proprietary and access-controlled; do not redistribute its library files. Market-data rights remain the responsibility of the project/provider. Lightweight Charts has separate open-source terms.

## Data-quality limitations
Most chart bugs that look like “TradingView data issues” are actually symbol/session/timezone/resolution/datafeed-contract mismatches. Preserve exchange timezone, session, price scale and monotonic bar timestamps.

## Copy guidance
See `../references/tradingview.md`, `../references/tradingview-runtime-kit.md`, `../references/chart-data-contract.md` and `../assets/tradingview/`. Freeze chart contract and project datafeed into the downstream project; do not depend on this Skill at runtime.