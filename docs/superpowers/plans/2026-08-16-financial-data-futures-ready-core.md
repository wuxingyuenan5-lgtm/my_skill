# financial-data Futures READY Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote official China futures daily contract market/settlement data into reusable READY helpers while preserving exchange-specific transport/parsing boundaries and one canonical futures row contract.

**Architecture:** Implement one explicit parser/fetch path per exchange inside `financial_data.cn_futures_official`, then normalize each provider payload into the same futures daily row. Reuse the existing `HttpClient` error model where HTTP transport applies, validate rows before returning them, and feed normalized rows directly into the existing dominant/curve/basis utilities.

**Tech Stack:** Python 3.9+, stdlib (`csv`, `io`, `zipfile`, `datetime`, `re`), `requests` through existing HTTP helpers, deterministic fixtures/fake sessions, pytest, Markdown/YAML capability documentation.

## Global Constraints

- Work only on `feat/financial-data-skill`; do not merge or force-rewrite `main`.
- Official exchange sources remain the source of record; wrappers may inform request shapes but are not declared as sources.
- `close`, `settlement`, and `pre_settlement` remain distinct; never substitute one for another.
- Provider failures/error pages must not be returned as successful empty datasets.
- Do not assume turnover units are identical across exchanges; preserve or explicitly convert only documented units.
- Summary rows (`小计`, `合计`, `总计`) are excluded at provider parsing.
- New READY labels require a real runtime function plus deterministic parser tests.
- Member rankings, warehouse/inventory, trading parameters and CTP intraday remain out of scope for this batch.

---

### Task 1: Canonical futures row and validation

**Files:**
- Create: `skills/financial-data/scripts/financial_data/cn_futures_official.py`
- Test: `skills/financial-data/tests/test_cn_futures_official.py`

**Interfaces:**
- Produces: `normalize_trade_date(value) -> str`, `validate_futures_daily_row(row) -> list[str]`, `_canonical_row(...) -> dict`.
- Consumers: all exchange parsers and dispatcher in later tasks.

- [ ] **Step 1: Write failing tests** proving required fields, OHLC consistency, non-negative volume/OI/turnover, and independent settlement fields.
- [ ] **Step 2: Run the focused test file** and confirm failure because the module/functions do not exist.
- [ ] **Step 3: Implement the minimal canonical-row helpers** with explicit source metadata and exchange/unit fields.
- [ ] **Step 4: Run focused tests** and confirm they pass.
- [ ] **Step 5: Commit through GitHub on the feature branch.**

### Task 2: SHFE + INE structured daily data

**Files:**
- Modify: `skills/financial-data/scripts/financial_data/cn_futures_official.py`
- Test: `skills/financial-data/tests/test_cn_futures_official.py`

**Interfaces:**
- Produces: `parse_shfe_daily_payload(payload, trade_date, source_url)`, `parse_ine_daily_payload(...)`, `fetch_shfe_daily(...)`, `fetch_ine_daily(...)`.

- [ ] **Step 1: Write failing fixtures/tests** for `o_curinstrument`, product-group fallback, summary filtering, EFP filtering, and malformed business payloads.
- [ ] **Step 2: Verify RED.**
- [ ] **Step 3: Implement parsers** mapping `OPENPRICE/HIGHESTPRICE/LOWESTPRICE/CLOSEPRICE/SETTLEMENTPRICE/PRESETTLEMENTPRICE/VOLUME/OPENINTEREST/TURNOVER` without cross-field substitution.
- [ ] **Step 4: Implement fetchers** using official SHFE/INE daily data URL families and existing HTTP error classification.
- [ ] **Step 5: Verify GREEN and commit.**

### Task 3: DCE + GFEX JSON POST data

**Files:**
- Modify: `skills/financial-data/scripts/financial_data/cn_futures_official.py`
- Test: `skills/financial-data/tests/test_cn_futures_official.py`

**Interfaces:**
- Produces: `parse_dce_daily_payload`, `parse_gfex_daily_payload`, `fetch_dce_daily`, `fetch_gfex_daily`.

- [ ] **Step 1: Write failing tests** for DCE `contractId/open/high/low/close/lastClear/clearPrice/volumn/openInterest/turnover` rows and GFEX `varietyOrder/delivMonth` rows.
- [ ] **Step 2: Verify RED.**
- [ ] **Step 3: Implement parsers** with explicit variety-code normalization and raw-row preservation.
- [ ] **Step 4: Implement POST transport** using official request families and explicit payloads; business failure raises `FinancialDataError`.
- [ ] **Step 5: Verify GREEN and commit.**

### Task 4: CFFEX historical ZIP/CSV daily rows

**Files:**
- Modify: `skills/financial-data/scripts/financial_data/cn_futures_official.py`
- Test: `skills/financial-data/tests/test_cn_futures_official.py`

**Interfaces:**
- Produces: `parse_cffex_daily_csv(text, trade_date, source_url, futures_only=False)`, `parse_cffex_history_zip(content, trade_date, ...)`, `fetch_cffex_daily(...)`.

- [ ] **Step 1: Write failing tests** for current CSV headers, summary-row exclusion, explicit option retention by default, and optional futures-only filtering.
- [ ] **Step 2: Verify RED.**
- [ ] **Step 3: Implement GB2312/GBK-safe ZIP/CSV parsing** and map CFFEX成交额 source unit `万元` explicitly.
- [ ] **Step 4: Implement historical-month ZIP fetch path** and missing-file failure semantics.
- [ ] **Step 5: Verify GREEN and commit.**

### Task 5: CZCE date-dependent text parser

**Files:**
- Modify: `skills/financial-data/scripts/financial_data/cn_futures_official.py`
- Test: `skills/financial-data/tests/test_cn_futures_official.py`

**Interfaces:**
- Produces: `parse_czce_daily_text(text, trade_date, source_url)`, `fetch_czce_daily(...)`.

- [ ] **Step 1: Write failing tests** for pipe-delimited current layout, commas in numbers, blank values, summary rows and provider error HTML.
- [ ] **Step 2: Verify RED.**
- [ ] **Step 3: Implement current-layout parser** with a strict header check and explicit `variety` extraction from contract code.
- [ ] **Step 4: Implement date-dependent official URL selection** for the supported modern history regime; unsupported historical regimes fail explicitly rather than guessing.
- [ ] **Step 5: Verify GREEN and commit.**

### Task 6: Dispatcher and analytics compatibility

**Files:**
- Modify: `skills/financial-data/scripts/financial_data/cn_futures_official.py`
- Modify: `skills/financial-data/scripts/financial_data/__init__.py`
- Test: `skills/financial-data/tests/test_cn_futures_official.py`

**Interfaces:**
- Produces: `fetch_cn_futures_daily(exchange, trade_date, **kwargs)` and public exports.

- [ ] **Step 1: Write failing dispatcher tests** for all six exchange codes and unsupported exchange errors.
- [ ] **Step 2: Verify normalized rows feed `select_dominant_contract()` and `term_structure()` without exchange-specific glue.**
- [ ] **Step 3: Implement dispatcher/public exports.**
- [ ] **Step 4: Run focused tests and commit.**

### Task 7: Capability catalog and handbook synchronization

**Files:**
- Modify: `skills/financial-data/references/capability-index.yaml`
- Modify: `skills/financial-data/references/futures-source-recipes.md`
- Modify: `skills/financial-data/references/futures-commodities.md`
- Modify: `skills/financial-data/README.md`

**Interfaces:**
- Produces machine-readable READY entries pointing to real runtime functions and precise unit/source notes.

- [ ] **Step 1: Split umbrella capability into six exchange capabilities.**
- [ ] **Step 2: Mark only exchange paths implemented and deterministically tested as READY.**
- [ ] **Step 3: Promote umbrella `cn_futures_daily_settlement` to READY only if all six exchange paths pass.**
- [ ] **Step 4: Document current official source pages, machine request families, turnover units, settlement semantics, and historical coverage boundaries.**
- [ ] **Step 5: Update README quick-start examples and commit.**

### Task 8: Verification and Draft PR refresh

- [ ] **Step 1: Run the fresh focused futures test suite.**
- [ ] **Step 2: Run full `skills/financial-data/tests` if a complete local tree is available; otherwise state exact tested subset.**
- [ ] **Step 3: AST-parse/compile all changed Python modules for Python 3.9 compatibility.**
- [ ] **Step 4: Compare feature branch to `main`, confirm no unintended paths and no new `main` write.**
- [ ] **Step 5: Update Draft PR #1 body with READY promotions, source/coverage limits and exact verification evidence.**
- [ ] **Step 6: Leave PR Draft and unmerged.**
