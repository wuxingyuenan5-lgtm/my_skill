# financial-data Handbook Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand `skills/financial-data` from a compact runtime foundation into a comprehensive cross-asset financial-data engineering handbook with copy-ready recipes, capability discovery, futures as a first-class asset class, TradingView/custom-chart delivery, and the useful capability union of `a-stock-data` and `global-stock-data`.

**Architecture:** Keep the standardized runtime (`DataRequest -> Route -> Fetch -> Normalize -> Validate`) for common reusable adapters, but treat the Skill itself as a durable handbook. Every data capability is discoverable through a machine-readable capability index and is classified as `READY` (runtime adapter), `RECIPE` (copy-ready implementation guidance), or `RESTRICTED` (technically documented but requiring license/key/permission). Downstream projects may export only the recipes they need and operate independently of this Skill afterward.

**Tech Stack:** Markdown/YAML handbook, Python 3.9+ standard library + `requests` runtime, HTML/JavaScript templates for TradingView/Lightweight Charts, optional FastAPI example for UDF, pytest fixtures for deterministic transformations where code is added.

## Global Constraints

- Work only on `feat/financial-data-skill`; never merge `main` automatically.
- `financial-data` is a handbook-first Skill; size is not a design constraint if navigation remains clear.
- Do not represent `RECIPE` or `RESTRICTED` capabilities as executable `READY` adapters.
- Every recipe must identify source, endpoint/access path, authentication, parameters, field map, units, time semantics, rate limits, known issues, fallback, compliance posture, and copy-ready implementation guidance where practical.
- Preserve canonical instrument IDs, provenance, explicit time fields, adjustment conventions, and volume units.
- Percentages are decimals internally.
- Futures are a first-class asset class with exact contract identity, trading-day/session semantics, contract master, continuous-series rules, curve/basis/positioning/warehouse/trading-parameter data.
- TradingView is a delivery/visualization layer, not a source abstraction. Keep Widget, Advanced Charts/Datafeed/UDF, Lightweight Charts, and Trading Platform/Broker integration separate.
- Do not redistribute TradingView Advanced Charts proprietary library files.
- Upstream source research may reference Apache-2.0 `simonlin1212/a-stock-data` and `simonlin1212/global-stock-data`; preserve attribution and do not silently copy large blocks without notice.
- Current source terms and provider behavior can change; record `last_verified` and never imply permanent permission.

---

### Task 1: Capability taxonomy and navigation

**Files:** `references/capability-index.yaml`, `references/capability-schema.md`, `SKILL.md`, `README.md`.

**Produces:** capability entries with `id`, `asset_class`, `market`, `dataset`, `status`, `primary_sources`, `fallback_sources`, `auth`, `compliance`, `reference`, and `runtime`.

- [ ] Define `READY`, `RECIPE`, `RESTRICTED` semantics.
- [ ] Expand the index to the A-share/global reference-repo union plus futures, TradingView, chart delivery and professional sources.
- [ ] Route agents through capability index first.
- [ ] Verify every `READY` entry maps to a real runtime module.

### Task 2: A-share handbook split by domain

**Files:** create `a-share-market-data.md`, `a-share-fundamentals.md`, `a-share-flows-positioning.md`, `a-share-microstructure.md`, `a-share-research-news.md`, `a-share-source-recipes.md`; modify `a-share.md`.

- [ ] Document K-line/order-book/ticks/quote/index/ETF recipes and adjustment/unit caveats.
- [ ] Document statements/F10/quarterly metrics/capital structure/research/consensus EPS.
- [ ] Document fund flow, margin, block trade, holder count, dividend, lockup, dragon-tiger and sector flow.
- [ ] Document limit-up/down/break-board/previous-limit/watchlist/anomaly pools, IRM and hot-list capabilities.
- [ ] Preserve BSE stale-code guards, field-index corrections, throttling and independent fallback rules.

### Task 3: US/HK/global equity handbook

**Files:** create `global-equity-market-data.md`, `global-equity-fundamentals.md`, `global-equity-events.md`; modify `us-hk.md`.

- [ ] Document US/HK quotes/K-lines and Yahoo cookie/crumb handling.
- [ ] Document valuation, analyst estimates, targets, institutional holdings and fund flow.
- [ ] Document market-wide list/search/news and event-calendar recipes.

### Task 4: SEC advanced official-data layer

**Files:** create `sec-edgar-advanced.md`; modify `adapters/sec_edgar.py`; add parser tests/fixtures.

- [ ] Add daily filing-index recipe/helper.
- [ ] Add EDGAR Frames cross-sectional recipe/helper.
- [ ] Document full-text search and filing-event workflows.
- [ ] Preserve declared User-Agent and rate-limit requirements.

### Task 5: Macro, positioning, short-volume and calendars

**Files:** create `macro-positioning-events.md`; add compact adapters/recipes for `cftc.py`, `finra.py`, `nasdaq_calendar.py`; update registry/tests.

- [ ] Cover CFTC COT, FINRA Reg SHO daily short volume and Nasdaq earnings calendar.
- [ ] Distinguish short volume from short interest.
- [ ] Keep source-use restrictions explicit.

### Task 6: Options and derivatives

**Files:** expand `derivatives.md`; create `us-options.md`, `china-etf-options.md`; add stable parser/runtime helpers where appropriate.

- [ ] Cover CBOE chain/Greeks/IV/0DTE/vol-OI flow and Yahoo fallback.
- [ ] Cover China ETF option contract list/T-quote/Greeks/IV.
- [ ] Normalize IV as decimals and separate provider Greeks from modeled Greeks.

### Task 7: Futures first-class handbook and utilities

**Files:** expand `futures-commodities.md`; create `futures-contract-master.md`, `futures-source-recipes.md`, `futures-curves-basis.md`, `futures-positioning-warehouse.md`, `futures-trading-parameters.md`; create `scripts/financial_data/futures.py` plus tests.

- [ ] Cover SHFE/INE, DCE, CZCE, CFFEX, GFEX official publication families and professional/CTP routes.
- [ ] Cover CME/CBOT/NYMEX/COMEX, ICE, LME and SGX source families at handbook level.
- [ ] Define exact-contract identity, dominant-contract selection, continuous-series methods, term structure, basis and spread normalization.
- [ ] Define night-session trading-date/calendar rules.
- [ ] Document warehouse/inventory/member positions/margin/limits/fees/delivery metadata.

### Task 8: TradingView and chart delivery kit

**Files:** expand `tradingview.md` and `chart-data-contract.md`; create `scripts/financial_data/charting.py`; create `assets/tradingview/widget.html`, `lightweight-chart.html`, `datafeed-template.js`, `udf-fastapi-example.py`; add transformation tests.

- [ ] Implement `to_tradingview_bar`, `to_lightweight_bar`, `to_udf_history`, resolution normalization and symbol-map guidance.
- [ ] Follow official Datafeed/UDF bar-order/time rules.
- [ ] Include real-time `subscribeBars` complete-bar semantics.
- [ ] Distinguish Pine Script from Advanced Charts JavaScript custom studies.
- [ ] Never include proprietary Advanced Charts library files.

### Task 9: Professional/licensed source handbook

**Files:** create `professional-data-sources.md`; update source/capability registries.

- [ ] Cover Wind, Choice, Bloomberg, LSEG/Refinitiv, Tushare Pro, CTP/broker feeds, exchange licensed L1/L2 and major crypto exchange APIs.
- [ ] Mark authentication/licensing as `RESTRICTED`; never commit credentials.
- [ ] Explain prototype-to-production source migration.

### Task 10: Project extraction protocol

**Files:** expand `project-export.md`; create `scripts/financial_data/project_export.py`, `assets/project-data-pack/README.template.md`; add manifest tests.

- [ ] Given capability IDs, emit a manifest of sources, fallbacks, dependencies, environment variables, recipe files and reusable modules.
- [ ] Preserve attribution/verification dates.
- [ ] Do not copy proprietary/restricted code or data silently.

### Task 11: Runtime integration and final index

**Files:** update `registry.py`, `facade.py`, adapters/package exports, README/SKILL/capability index.

- [ ] Register only adapters that actually exist.
- [ ] Replace stale `planned later` messages when implemented.
- [ ] Add examples for A-share dashboard, futures monitor, SEC screener, options flow and TradingView custom-data projects.

### Task 12: Verification and PR update

- [ ] Run deterministic parser/helper tests where code is added.
- [ ] Validate Skill frontmatter/path constraints and READY-to-runtime mappings.
- [ ] Update Draft PR #1 to describe handbook-first scope and exact READY/RECIPE/RESTRICTED boundary.
- [ ] Fast-forward `feat/financial-data-skill` to the reviewed expansion result.
- [ ] Do not merge `main`.

## Self-review

Coverage includes all user-requested reference-repo capabilities, futures, TradingView/custom data, professional sources and project extraction. Runtime additions remain behind existing `DataPoint`/`DataResult` contracts; handbook-only capabilities are explicitly separated from executable adapters.