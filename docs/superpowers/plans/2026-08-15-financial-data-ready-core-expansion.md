# financial-data READY Core Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote stable, high-frequency market-data and provider-discovery recipes to tested READY helpers while preserving the handbook-first architecture.

**Architecture:** Add small market-data adapters for Tencent A-share K-lines and Yahoo US/HK chart data. Add a provider-level Eastmoney toolkit for datacenter/Push2/discovery rather than wiring every Eastmoney dataset into the common facade. Promote capability statuses only when code and deterministic tests exist.

**Tech Stack:** Python 3.9+, `requests`, existing `HttpClient`, `DataPoint`/`DataRequest`/`DataResult`, deterministic fixture/fake-session tests, Markdown/YAML capability documentation.

## Global Constraints

- Work only on `feat/financial-data-skill`; do not merge `main`.
- Preserve current handbook-first READY/RECIPE/RESTRICTED semantics.
- Percentages remain decimals internally.
- Provider failures must not be represented as successful empty data.
- Keep research-only/provider-term caveats for Tencent/Yahoo/Eastmoney.
- No proprietary credentials or licensed market data in the repository.
- New READY labels require real code paths and deterministic tests.

---

### Task 1: Tencent K-line READY helper

**Files:** modify `adapters/tencent.py`, `adapters/__init__.py`; test `tests/test_market_data_ready.py`.

**Produces:** `parse_tencent_kline_payload(...)` and `TencentAdapter.fetch(... field='kline')`.

- [x] Write failing daily/minute parser tests and unsupported-resolution test.
- [x] Implement daily/minute URL construction and normalized `bar` DataPoints.
- [x] Verify the deterministic tests pass.

### Task 2: Yahoo US/HK K-line READY adapter

**Files:** create `adapters/yahoo_chart.py`; modify `adapters/__init__.py`; test `tests/test_market_data_ready.py`.

**Produces:** `YahooChartAdapter`, `parse_yahoo_chart_payload(...)`.

- [x] Write failing chart parser tests including null rows and provider error payload.
- [x] Implement US/HK symbol mapping and interval/range parameters.
- [x] Return normalized `bar` DataPoints with exchange timezone metadata.
- [x] Verify the deterministic tests pass.

### Task 3: Eastmoney provider toolkit

**Files:** create `financial_data/eastmoney.py`; test `tests/test_eastmoney_ready.py`.

**Produces:** `EastmoneyClient.datacenter_query`, `push2_list`, `market_stock_list`, `search_securities`.

- [x] Write failing datacenter success/business-error tests.
- [x] Write failing Push2 market-list/discovery normalization tests.
- [x] Implement provider helper with conservative serialized throttle and existing HTTP classification.
- [x] Preserve raw provider rows in normalized output.
- [x] Verify the deterministic tests pass.

### Task 4: Runtime/catalog integration

**Files:** modify `facade.py`, `registry.py`, `routing.py`, `__init__.py`, `capability-index.yaml`, market-data/provider docs and README.

- [x] Register Yahoo K-line adapter in `default_adapters()`.
- [x] Keep Eastmoney toolkit directly callable rather than routing arbitrary datasets through `get_data()`.
- [x] Add K-line routing preferences and structured-bar OHLCV validation.
- [x] Promote only implemented capabilities to READY.
- [x] Keep full A-share cross-section RECIPE until BSE universe semantics are explicitly frozen.
- [x] Document supported resolutions, limits and research-use caveats.

### Task 5: Verification and PR refresh

- [x] Run the current READY-core deterministic test subset: **11 passed**.
- [x] Run Python 3.9 AST/compile checks for Tencent K-line, Yahoo Chart and EastmoneyClient modules.
- [x] Compare feature branch to `main` and inspect scope.
- [x] Record that a complete local Git checkout was unavailable, so no new claim of a full repository pytest run is made.
- [ ] Refresh Draft PR #1 with exact READY promotions and verification evidence.
- [x] Keep PR Draft and do not merge `main`.
