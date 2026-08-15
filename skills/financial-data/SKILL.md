---
name: financial-data
description: Use when a task needs financial-market data sources, retrieval recipes, normalization, source routing, provenance, fallback, project-local data modules, TradingView visualization, or reproducible derived metrics across equities, futures, options, funds, rates, macro, FX or crypto.
---

# financial-data

## Identity

This Skill is an intentionally comprehensive **cross-asset financial-data engineering handbook, source recipe library and reusable utility kit**. A downstream project normally consults it during setup, extracts only the capabilities it needs, then owns those adapters/data workflows independently.

Core chain: **Discover → Identify → Route → Fetch → Normalize → Validate → Export/Deliver**.

## Start with discovery

Search `references/capability-index.yaml` first. Status meanings are defined in `references/capability-schema.md`:

- `READY`: shared adapter/helper/template exists now.
- `RECIPE`: complete project-copy guidance exists; common facade is optional.
- `RESTRICTED`: key/license/entitlement/permission is required.
- `DEGRADED`: provider is known to be unreliable; use fallback.
- `DEPRECATED`: migration/history only.

Never promote a documented recipe to READY unless the referenced runtime actually exists.

## Operating rules

1. Resolve canonical instrument identity before provider aliases; never guess ambiguous symbols.
2. Route by **asset class + market + dataset + intended usage**, not by one global favorite provider.
3. Keep facts, vendor estimates, sentiment/editorial tags and locally derived values as separate data classes.
4. Preserve source/provenance, `as_of`, `retrieved_at`, unit/currency and relevant trade/report/publish/available dates.
5. Percentages are decimals internally. Declare adjustment, volume unit, futures multiplier and settlement-vs-close semantics.
6. Important vendor-derived data should use an independent cross-check when practical; surface `SOURCE_CONFLICT` rather than silently selecting one value.
7. Fallback should cross domains/rate-limit planes. Provider failure is not equivalent to “no data.”
8. Preserve provider quirks, field-map corrections, stale-symbol warnings, known-dead endpoints and throttle rules when they prevent silent errors.
9. Re-check data rights before commercial use or redistribution. Never bypass CAPTCHA/access controls/explicit anti-bot restrictions.
10. Prefer deterministic local calculation for indicators, returns, curve/basis/continuous-series transformations and record methodology.
11. For recurring project use, follow `references/project-export.md`: copy only selected recipes/modules/assets into the downstream project.

## Two navigation modes

### By required data
Use `capability-index.yaml`, then open the referenced domain page.

### By provider
Start with `provider-recipe-kit.md` or `source-recipes/` for Tencent/Sina/mootdx, Eastmoney, CNINFO/exchanges/THS, SEC/Yahoo/US providers.

To audit whether the two reference repositories were preserved, read `reference-repo-coverage.md`.

## Handbook map

### China equities
`a-share.md` → `a-share-market-data.md`, `a-share-fundamentals.md`, `a-share-flows-positioning.md`, `a-share-microstructure.md`, `a-share-research-news.md`, `a-share-source-recipes.md`.

### US/HK/global equities
`us-hk.md` → `global-equity-market-data.md`, `global-equity-fundamentals.md`, `global-equity-events.md`, `sec-edgar-advanced.md`, `macro-positioning-events.md`.

### Futures/commodities
`futures-commodities.md`, `futures-contract-master.md`, `futures-source-recipes.md`, `futures-curves-basis.md`, `futures-positioning-warehouse.md`, `futures-trading-parameters.md`.

### Options
`derivatives.md`, `us-options.md`, `china-etf-options.md`.

### Macro / funds / FX / crypto
`macro-global.md`, `macro-rates.md`, `funds-etf.md`, `fx-crypto.md`.

### Reference-data correctness
`industry-classification.md`, `trading-calendar.md`, `point-in-time-vintage.md`, `instrument-master.md`, `market-conventions.md`, `data-contract.md`.

### Sources / quality / licensing
`source-registry.md`, `source-routing.md`, `fallback-policy.md`, `validation-rules.md`, `compliance.md`, `professional-data-sources.md`, `provider-recipe-kit.md`.

### Visualization / extraction
`chart-data-contract.md`, `tradingview.md`, `tradingview-runtime-kit.md`, `project-export.md`.

## Reusable utilities

```python
from financial_data import DataRequest, get_data, result_dict
from financial_data.charting import to_tradingview_bar, to_udf_history, to_lightweight_bar
from financial_data.futures import select_dominant_contract, term_structure, calendar_spread, basis, roll_adjustment
from financial_data.project_export import build_project_manifest, render_manifest_markdown
```

Shared `get_data()` is a convenience runtime for selected READY adapters; it is not the boundary of handbook coverage.

## Futures invariant

Exact contracts, dominant contracts and continuous series are different instruments. Preserve exchange trading day for night sessions, settlement separately from close, contract multiplier/unit, expiry and explicit roll/adjustment methodology.

## TradingView invariant

Do not call everything a “TradingView API.” Widgets display TradingView-supplied data; Advanced Charts displays project data through Datafeed/UDF; Lightweight Charts renders project data with an open-source chart library; Trading Platform/Broker API adds execution; Pine Script on tradingview.com is a separate indicator environment. TradingView is primarily a visualization/integration layer here, not an unofficial generic data scraper.
