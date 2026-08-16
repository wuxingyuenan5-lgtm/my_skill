# financial-data Futures Positioning READY Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote official China futures member ranking data into reusable READY helpers with long-form facts, explicit publication status, and deterministic Top-N derived analytics.

**Architecture:** Keep SHFE/INE/DCE/CZCE/CFFEX/GFEX provider parsing isolated, normalize provider rows into one long-form ranking fact schema, then derive Top5/10/20 metrics in a provider-agnostic analytics layer. Empty data is not automatically failure: fetch results carry publication status so threshold-based non-publication can be distinguished from source failure.

**Tech Stack:** Python 3.9+, stdlib (`csv`, `io`, `re`, `html`, `datetime`), existing `HttpClient`, pytest deterministic fixtures/fakes, Markdown/YAML capability documentation.

## Global Constraints

- Work only on `feat/financial-data-skill`; do not merge or force-rewrite `main`.
- Official exchange sources are the source of record; wrappers may inform request shapes but are not declared sources.
- Internal canonical storage is long-form: one row is one ranking type/member/rank observation.
- `volume`, `long_open_interest`, and `short_open_interest` rankings are independent lists; do not align them by rank into a fake common member row.
- Preserve provider member names; normalized aliases are optional metadata, not destructive replacements.
- Distinguish `published`, `not_published_by_rule`, `no_trading`, and `source_failure` when the source semantics allow it.
- Top-N net long/short is derived from disclosed ranking subsets and must never be described as full-market net positioning.
- Concentration requires an explicit same-scope denominator; do not calculate it from ranking rows alone.
- Warehouse/inventory, trading parameters, delivery data and CTP intraday remain out of scope.
- READY requires a real runtime function, deterministic parser tests, documented source semantics and explicit error/publication handling.

---

### Task 1: Canonical ranking fact and result contract

**Files:**
- Create: `skills/financial-data/scripts/financial_data/futures_positioning.py`
- Create: `skills/financial-data/tests/test_futures_positioning.py`

**Interfaces:**
- Produces: `make_ranking_fact(...) -> dict`, `validate_ranking_fact(row) -> list[str]`, `positioning_result(exchange, trade_date, status, rows, ...) -> dict`.

- [ ] **Step 1: Write failing tests** for required keys, `ranking_type in {volume,long,short}`, rank > 0, non-negative value, signed change, and publication statuses.
- [ ] **Step 2: Run focused tests and verify RED** because the module does not exist.
- [ ] **Step 3: Implement minimal canonical helpers** with `trade_date/exchange/scope_type/scope_id/variety/contract_id/ranking_type/rank/member/value/change/source_id/source_url/raw`.
- [ ] **Step 4: Run focused tests and verify GREEN.**
- [ ] **Step 5: Commit on `feat/financial-data-skill`.**

### Task 2: SHFE and INE ranking parsers/fetchers

**Files:**
- Modify: `skills/financial-data/scripts/financial_data/futures_positioning.py`
- Test: `skills/financial-data/tests/test_futures_positioning.py`

**Interfaces:**
- Produces: `parse_shfe_position_payload`, `fetch_shfe_positions`, `parse_ine_position_payload`, `fetch_ine_positions`.

- [ ] **Step 1: Add failing fixtures/tests** for `o_cursor`-style records, summary rows, contract/product identifiers, member abbreviations and volume/long/short ranking fields.
- [ ] **Step 2: Verify RED.**
- [ ] **Step 3: Implement SHFE parser/fetcher** using the official current `pmYYYYMMDD.dat` family and preserving disclosure status metadata.
- [ ] **Step 4: Implement INE only after its official/current machine path and field schema are explicitly verified; otherwise leave the INE capability RECIPE/DEGRADED rather than guessing.**
- [ ] **Step 5: Verify GREEN for implemented paths and commit.**

### Task 3: DCE and GFEX ranking parsers/fetchers

**Files:**
- Modify: `skills/financial-data/scripts/financial_data/futures_positioning.py`
- Test: `skills/financial-data/tests/test_futures_positioning.py`

**Interfaces:**
- Produces: `parse_dce_position_payload`, `fetch_dce_positions`, `parse_gfex_position_payload`, `fetch_gfex_positions`.

- [ ] **Step 1: Add failing tests** for contract discovery + member ranking rows, independent volume/long/short lists, and provider business-error payloads.
- [ ] **Step 2: Verify RED.**
- [ ] **Step 3: Implement DCE source flow** without relying on a pandas/BeautifulSoup runtime dependency in the shared core.
- [ ] **Step 4: Implement GFEX POST flow** around official member-position endpoints with explicit contract/variety scope.
- [ ] **Step 5: Verify GREEN and commit.**

### Task 4: CFFEX and CZCE ranking parsers/fetchers

**Files:**
- Modify: `skills/financial-data/scripts/financial_data/futures_positioning.py`
- Test: `skills/financial-data/tests/test_futures_positioning.py`

**Interfaces:**
- Produces: `parse_cffex_position_csv`, `fetch_cffex_positions`, `parse_czce_position_text`, `fetch_czce_positions`.

- [ ] **Step 1: Add failing tests** for CFFEX CSV ranking rows, options/futures scope retention, summary rows and explicit disclosure/no-publication semantics.
- [ ] **Step 2: Add failing tests** for CZCE modern holding text/HTML layout, commas, blank values and error pages.
- [ ] **Step 3: Implement provider parsers/fetchers** with historical-regime boundaries documented rather than silently guessed.
- [ ] **Step 4: Verify GREEN and commit.**

### Task 5: Provider-agnostic Top-N analytics

**Files:**
- Modify: `skills/financial-data/scripts/financial_data/futures_positioning.py`
- Test: `skills/financial-data/tests/test_futures_positioning.py`

**Interfaces:**
- Produces: `aggregate_top_n(rows, n, denominator=None) -> dict`, `aggregate_standard_windows(rows, denominators=None) -> dict`.

- [ ] **Step 1: Write failing tests** for Top5/10/20 sums by ranking type, change sums, `long_minus_short`, missing denominator behavior and valid concentration calculations.
- [ ] **Step 2: Verify RED.**
- [ ] **Step 3: Implement aggregation** using only rows with rank <= N and matching exchange/trade_date/scope.
- [ ] **Step 4: Assert concentration is absent/None without an explicit matching denominator and present only when denominator > 0.**
- [ ] **Step 5: Verify GREEN and commit.**

### Task 6: Dispatcher, exports and daily-market denominator bridge

**Files:**
- Modify: `skills/financial-data/scripts/financial_data/futures_positioning.py`
- Modify: `skills/financial-data/scripts/financial_data/__init__.py`
- Test: `skills/financial-data/tests/test_futures_positioning.py`

**Interfaces:**
- Produces: `fetch_cn_futures_positions(exchange, trade_date, **kwargs)` and `position_denominators_from_daily(rows, contract_id) -> dict`.

- [ ] **Step 1: Add failing dispatcher tests** for supported READY exchanges and unsupported codes.
- [ ] **Step 2: Add denominator bridge tests** using v0.2.2 canonical daily rows: total volume for volume concentration and open interest for long/short concentration.
- [ ] **Step 3: Implement exports/dispatcher/bridge.**
- [ ] **Step 4: Verify GREEN and commit.**

### Task 7: Capability Index and handbook synchronization

**Files:**
- Modify: `skills/financial-data/references/capability-index.yaml`
- Modify: `skills/financial-data/references/futures-positioning-warehouse.md`
- Create: `skills/financial-data/references/futures-positioning-ready-core.md`
- Modify: `skills/financial-data/references/futures-source-recipes.md`
- Modify: `skills/financial-data/README.md`

- [ ] **Step 1: Add exchange-level positioning capabilities** and point READY entries only to real runtime functions.
- [ ] **Step 2: Promote umbrella `cn_futures_member_positions` only if all six exchanges satisfy READY criteria; otherwise keep umbrella RECIPE and expose partial READY exchange entries.**
- [ ] **Step 3: Document disclosure thresholds/publication status and explicitly state ranking subsets are not full-market positioning.**
- [ ] **Step 4: Document Top-N formulas and denominator requirements.**
- [ ] **Step 5: Bump Capability Index version and README version only after runtime/tests support the new status.**

### Task 8: Verification and Draft PR refresh

- [ ] **Step 1: Run fresh focused positioning tests.**
- [ ] **Step 2: Run existing v0.2.2 futures daily tests together with positioning tests to catch integration regressions.**
- [ ] **Step 3: Run Python 3.9 AST/compile checks on changed Python modules.**
- [ ] **Step 4: Verify every positioning READY runtime in Capability Index imports and is callable.**
- [ ] **Step 5: Compare `feat/financial-data-skill` to `main` and confirm no unintended paths / no new main write.**
- [ ] **Step 6: Update Draft PR #1 with exact READY/RECIPE status per exchange and exact fresh test evidence.**
- [ ] **Step 7: Leave PR Draft and unmerged.**
