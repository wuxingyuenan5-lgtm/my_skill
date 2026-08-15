---
name: financial-data
description: Use when a task needs financial-market data sources, retrieval recipes, normalization, source routing, provenance, fallback, project-local data modules, TradingView visualization, or reproducible derived metrics across equities, futures, options, rates, macro, FX or crypto.
---

# financial-data

## Identity

This Skill is a **cross-asset financial-data engineering handbook, recipe library and reusable utility kit**. It is intentionally comprehensive. A downstream project usually consults it during setup, extracts only the capabilities it needs, then owns those adapters independently.

Core chain: **Discover → Identify → Route → Fetch → Normalize → Validate → Export/Deliver**.

## Always start with capability discovery

Read/search `references/capability-index.yaml` first. Each capability is one of:

- `READY` — shared adapter/helper/template exists now.
- `RECIPE` — complete copy-ready integration guidance exists; common facade is optional.
- `RESTRICTED` — key/license/entitlement/permission is required.
- `DEGRADED` — known provider problem; use documented fallback.
- `DEPRECATED` — historical/migration reference only.

Never promote a `RECIPE` to `READY` just because the source is well documented.

## Operating contract

1. Resolve canonical instrument identity before provider aliases. Never guess ambiguous symbols.
2. Route by **asset class + market + dataset + usage**. Facts, vendor estimates, sentiment/editorial tags and locally derived values are separate classes.
3. Preserve provenance, `as_of`, `retrieved_at`, units/currency and relevant trade/report/publish/available dates.
4. Percentages are decimals internally. Price adjustment, futures contract multiplier, volume unit and settlement/close choice must be explicit.
5. For important vendor-derived data, cross-check an independent source where practical. Surface `SOURCE_CONFLICT`; do not silently pick a convenient number.
6. Fallback should cross domains/rate-limit planes. Provider failure is not “no data.”
7. Preserve rate-limit rules, parser quirks, dead endpoints, corrected field mappings and stale-code warnings if they prevent future silent errors.
8. Check current data rights before commercial use/redistribution. Never bypass access controls, CAPTCHA or explicit anti-bot restrictions.
9. Prefer deterministic local calculations for indicators/returns/curves/basis/continuous-series transformations and record methodology.
10. For recurring project use, follow `references/project-export.md`: copy only selected recipes/modules into the project rather than making every refresh call this Skill.

## Handbook map

### A-shares
`a-share.md` → market data, fundamentals, flows/positioning, microstructure, research/news and source recipes.

### US/HK/global equities
`us-hk.md` → market data, fundamentals, SEC advanced, events, CFTC/FINRA and options.

### Futures/commodities
`futures-commodities.md` plus `futures-contract-master.md`, `futures-source-recipes.md`, `futures-curves-basis.md`, `futures-positioning-warehouse.md`, `futures-trading-parameters.md`.

### Options
`derivatives.md`, `us-options.md`, `china-etf-options.md`.

### Professional/licensed sources
`professional-data-sources.md`.

### Visualization / project delivery
`chart-data-contract.md`, `tradingview.md`, `project-export.md`.

### Core semantics
`data-contract.md`, `instrument-master.md`, `market-conventions.md`, `source-registry.md`, `source-routing.md`, `fallback-policy.md`, `validation-rules.md`, `compliance.md`, `workflows.md`.

## Runtime/toolkit

Common Python lives in `scripts/financial_data/`. The shared `get_data()` facade is a convenience layer, not the definition of Skill coverage.

Chart transforms:

```python
from financial_data.charting import to_tradingview_bar, to_udf_history, to_lightweight_bar
```

Futures methodology helpers:

```python
from financial_data.futures import select_dominant_contract, term_structure, calendar_spread, basis, roll_adjustment
```

Project extraction:

```python
from financial_data.project_export import build_project_manifest
```

## Futures invariant

Exact contracts, dominant contracts and continuous series are different instruments. Preserve exchange trading day for night sessions, settlement separately from close, and explicit roll/adjustment methodology.

## TradingView invariant

Do not call everything a “TradingView API.”

- Widgets display TradingView-supplied data.
- Advanced Charts displays project data through Datafeed API/UDF; its proprietary library files are not redistributed here.
- Lightweight Charts renders project data with an open-source chart library.
- Trading Platform/Broker API is trading integration.
- Pine Script on tradingview.com is a separate indicator environment from Advanced Charts JavaScript custom studies.

Raw financial data should come from the appropriate exchange/vendor/source recipe; TradingView is primarily the visualization/integration layer.
