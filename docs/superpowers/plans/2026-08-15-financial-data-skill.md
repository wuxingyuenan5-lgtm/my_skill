# financial-data Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `skills/financial-data` v0.1.0 as a reusable financial-data foundation that identifies instruments, routes requests to appropriate sources, normalizes and validates results with provenance, supports independent fallback, computes deterministic derived metrics locally, and exposes a concise Agent-facing Skill.

**Architecture:** Keep `SKILL.md` thin and declarative. Put long market/source rules in `references/`; reusable Python logic in focused `scripts/` modules; adapters behind a common `SourceAdapter` interface; tests use fixtures by default and a small optional live-smoke layer. The public Python facade is `financial_data.py`, which composes instrument resolution, routing, adapter execution, normalization, validation, output compression, and explicit error reporting.

**Tech Stack:** Python 3.9+ standard library + `requests`; `pytest` for tests. No required pandas/akshare/mootdx dependency in v0.1.0. Optional adapters may document extra dependencies but core imports must remain lightweight.

## Global Constraints

- Skill directory: `skills/financial-data/`; frontmatter `name` must equal `financial-data`.
- Initial version: `0.1.0`.
- Core flow: `Identify -> Route -> Fetch -> Normalize -> Validate -> Cite -> Deliver`.
- Internal percentages are decimals (`3.21% -> 0.0321`).
- Every successful standardized datum carries provenance, `as_of`, and `retrieved_at`.
- Distinguish `trade_date`, `calendar_date`, `report_period`, `publish_date`, `as_of`, and `retrieved_at`.
- Price series must declare `raw`, `forward_adjusted`, `backward_adjusted`, or `total_return_adjusted` where applicable.
- Volume-like fields must declare `shares`, `lots`, or `contracts`.
- Routing is field-level, not source-global.
- Fallback should move across independent domains/rate-limit planes where possible.
- Source conflicts must surface as `SOURCE_CONFLICT`; never silently pick a convenient value.
- Do not hard-code API keys, cookies, SEC contact identity, or private credentials.
- Do not bypass CAPTCHA, access controls, or explicit anti-bot restrictions.
- Deterministic derived metrics should be computed locally.
- Core v0.1.0 must not require a persistent market-data database.
- `python3 scripts/validate_skills.py` must pass before completion.

## File Structure

Create or modify the following files:

```text
README.md                                      # add skill index entry
skills/financial-data/SKILL.md                # thin Agent contract and routing guide
skills/financial-data/README.md               # installation, capabilities, examples, limitations
skills/financial-data/agents/openai.yaml      # UI/agent metadata matching repository convention
skills/financial-data/references/data-contract.md
skills/financial-data/references/instrument-master.md
skills/financial-data/references/source-registry.md
skills/financial-data/references/source-routing.md
skills/financial-data/references/validation-rules.md
skills/financial-data/references/market-conventions.md
skills/financial-data/references/compliance.md
skills/financial-data/references/fallback-policy.md
skills/financial-data/references/workflows.md
skills/financial-data/references/a-share.md
skills/financial-data/references/us-hk.md
skills/financial-data/references/macro-rates.md
skills/financial-data/references/futures-commodities.md
skills/financial-data/references/derivatives.md
skills/financial-data/scripts/__init__.py
skills/financial-data/scripts/contracts.py
skills/financial-data/scripts/instruments.py
skills/financial-data/scripts/registry.py
skills/financial-data/scripts/routing.py
skills/financial-data/scripts/validation.py
skills/financial-data/scripts/normalize.py
skills/financial-data/scripts/indicators.py
skills/financial-data/scripts/source_health.py
skills/financial-data/scripts/financial_data.py
skills/financial-data/scripts/adapters/__init__.py
skills/financial-data/scripts/adapters/base.py
skills/financial-data/scripts/adapters/tencent.py
skills/financial-data/scripts/adapters/sec_edgar.py
skills/financial-data/scripts/adapters/treasury.py
skills/financial-data/tests/test_contracts.py
skills/financial-data/tests/test_instruments.py
skills/financial-data/tests/test_registry_routing.py
skills/financial-data/tests/test_normalize_validation.py
skills/financial-data/tests/test_indicators.py
skills/financial-data/tests/test_facade.py
skills/financial-data/tests/fixtures/tencent_quote.json
skills/financial-data/tests/fixtures/sec_companyfacts.json
skills/financial-data/tests/fixtures/treasury_yield.json
```

---

### Task 1: Core contracts and explicit error model

**Files:**
- Create: `skills/financial-data/scripts/contracts.py`
- Test: `skills/financial-data/tests/test_contracts.py`

**Interfaces:**
- Produces: `DataRequest`, `DataPoint`, `DataResult`, `FinancialDataError`, `ErrorCode`, `QualityFlag`.
- Later tasks consume these exact types.

- [ ] **Step 1: Write failing contract tests**

```python
from datetime import datetime, timezone
from skills.financial_data.scripts.contracts import DataPoint, ErrorCode, FinancialDataError


def test_datapoint_requires_provenance():
    point = DataPoint(
        instrument_id="equity_cn_600519",
        symbol="600519.SH",
        field="turnover",
        value=6_830_000_000,
        unit="CNY",
        currency="CNY",
        as_of="2026-08-14T15:00:00+08:00",
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        source_id="tencent",
        source_type="secondary",
        status="verified",
    )
    assert point.source_id == "tencent"
    assert point.quality_flags == []


def test_error_code_is_stable():
    err = FinancialDataError(ErrorCode.SOURCE_CONFLICT, "values disagree")
    assert err.code.value == "SOURCE_CONFLICT"
```

- [ ] **Step 2: Run the focused test and verify failure**

Run: `python -m pytest skills/financial-data/tests/test_contracts.py -q`
Expected: import/module failure because contracts do not exist.

- [ ] **Step 3: Implement minimal typed dataclasses and enums**

```python
class ErrorCode(str, Enum):
    INSTRUMENT_NOT_FOUND = "INSTRUMENT_NOT_FOUND"
    FIELD_NOT_SUPPORTED = "FIELD_NOT_SUPPORTED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    SOURCE_BLOCKED = "SOURCE_BLOCKED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    RATE_LIMITED = "RATE_LIMITED"
    STALE_DATA = "STALE_DATA"
    NORMALIZATION_ERROR = "NORMALIZATION_ERROR"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    SOURCE_CONFLICT = "SOURCE_CONFLICT"
    COMPLIANCE_RESTRICTED = "COMPLIANCE_RESTRICTED"
```

Define dataclasses with immutable defaults via `field(default_factory=list)` and a `to_dict()` method for Agent-safe serialization. `DataRequest` fields: `instrument`, `field`, optional `market`, `start`, `end`, `as_of`, `output_profile="standard"`, `require_crosscheck=False`. `DataResult` fields: `data`, `errors`, `sources_used`, `fallbacks_used`, `status`.

- [ ] **Step 4: Run tests and confirm pass**

Run: `python -m pytest skills/financial-data/tests/test_contracts.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/financial-data/scripts/contracts.py skills/financial-data/tests/test_contracts.py
git commit -m "feat(financial-data): add data contracts and errors"
```

---

### Task 2: Instrument Master and canonical identifiers

**Files:**
- Create: `skills/financial-data/scripts/instruments.py`
- Create: `skills/financial-data/references/instrument-master.md`
- Test: `skills/financial-data/tests/test_instruments.py`

**Interfaces:**
- Consumes: `FinancialDataError`, `ErrorCode`.
- Produces: `Instrument`, `InstrumentMaster.resolve(query: str, market: str | None = None) -> Instrument`, `normalize_symbol(query: str, market: str | None = None) -> str`.

- [ ] **Step 1: Write failing resolution tests**

```python
from skills.financial_data.scripts.instruments import InstrumentMaster


def test_resolve_a_share_suffixes():
    master = InstrumentMaster()
    assert master.resolve("600519").ticker == "600519.SH"
    assert master.resolve("000001").ticker == "000001.SZ"


def test_resolve_hk_padding():
    master = InstrumentMaster()
    assert master.resolve("700.HK").ticker == "0700.HK"


def test_resolve_us_ticker():
    master = InstrumentMaster()
    assert master.resolve("AAPL").ticker == "AAPL.US"
```

- [ ] **Step 2: Run and verify failure**

Run: `python -m pytest skills/financial-data/tests/test_instruments.py -q`
Expected: module/function failure.

- [ ] **Step 3: Implement deterministic v0.1.0 normalization**

Rules:
- Six-digit CN symbols beginning `5/6/9` default SSE; `0/1/2/3` default SZSE; `4/8` default BSE.
- `.SH`, `.SZ`, `.BJ`, `.HK`, `.US` inputs are preserved after normalization.
- HK numeric symbols are zero-padded to four digits before `.HK`.
- Alphabetic 1-5 character tickers default `.US` unless market overrides.
- Unknown/ambiguous strings raise `INSTRUMENT_NOT_FOUND`; do not fuzzy-guess company names in v0.1.0.

Define `Instrument` fields: `canonical_id`, `symbol`, `exchange`, `ticker`, `name`, `asset_class`, `currency`, `country`, `aliases`, `external_ids`.

- [ ] **Step 4: Run tests and confirm pass**

Run: `python -m pytest skills/financial-data/tests/test_instruments.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/financial-data/scripts/instruments.py skills/financial-data/references/instrument-master.md skills/financial-data/tests/test_instruments.py
git commit -m "feat(financial-data): add instrument master"
```

---

### Task 3: Source registry, health state, compliance metadata, and field-level routing

**Files:**
- Create: `skills/financial-data/scripts/registry.py`
- Create: `skills/financial-data/scripts/source_health.py`
- Create: `skills/financial-data/scripts/routing.py`
- Create: `skills/financial-data/references/source-registry.md`
- Create: `skills/financial-data/references/source-routing.md`
- Create: `skills/financial-data/references/compliance.md`
- Create: `skills/financial-data/references/fallback-policy.md`
- Test: `skills/financial-data/tests/test_registry_routing.py`

**Interfaces:**
- Produces: `SourceSpec`, `SourceHealth`, `SourceRegistry`, `Router.route(request, instrument) -> list[SourceSpec]`.
- `SourceSpec` exact fields: `source_id`, `domains`, `markets`, `fields`, `authority`, `reliability`, `freshness`, `compliance`, `commercial_use`, `redistribution`, `auth`, `rate_limit`, `status`, `last_verified`, `independence_group`, `adapter`.

- [ ] **Step 1: Write failing routing tests**

```python
from skills.financial_data.scripts.contracts import DataRequest
from skills.financial_data.scripts.instruments import InstrumentMaster
from skills.financial_data.scripts.registry import default_registry
from skills.financial_data.scripts.routing import Router


def test_sec_wins_for_us_filings():
    inst = InstrumentMaster().resolve("AAPL")
    routes = Router(default_registry()).route(DataRequest("AAPL", "filings"), inst)
    assert routes[0].source_id == "sec_edgar"


def test_cn_quote_prefers_tencent_over_eastmoney():
    inst = InstrumentMaster().resolve("600519")
    routes = Router(default_registry()).route(DataRequest("600519", "quote"), inst)
    assert routes[0].source_id == "tencent"


def test_fallback_changes_independence_group():
    inst = InstrumentMaster().resolve("600519")
    routes = Router(default_registry()).route(DataRequest("600519", "quote"), inst)
    assert routes[0].independence_group != routes[1].independence_group
```

- [ ] **Step 2: Run and verify failure**

Run: `python -m pytest skills/financial-data/tests/test_registry_routing.py -q`
Expected: missing registry/routing modules.

- [ ] **Step 3: Implement registry and score function**

Use a deterministic numeric routing score:

```python
score = (
    authority_score * 0.30
    + reliability_score * 0.25
    + freshness_score * 0.20
    + compliance_score * 0.15
    + health_score * 0.10
)
```

Map grades `A/B/C/D` to `1.0/0.75/0.5/0.25`. Exclude `broken`, `blocked`, and `deprecated` sources from normal routes. Add explicit field overrides so `filings + US -> sec_edgar`, `yield_curve + US -> treasury`, `quote + CN -> tencent` before generic scoring.

Seed registry with metadata for `tencent`, `sina`, `eastmoney`, `cninfo`, `sse_szse`, `sec_edgar`, `treasury`, `cftc`, `yahoo`, `cboe`, `finra`. Only adapters implemented in v0.1.0 are executable; other sources may be registry-only and marked `adapter=None`.

- [ ] **Step 4: Implement health updates**

`SourceHealthTracker.record_success(source_id, at)` sets healthy unless manually blocked/deprecated. `record_failure(source_id, reason, at)` increments consecutive failures; 1-2 failures -> degraded, >=3 -> broken. Keep this in-memory in v0.1.0; no persistence requirement.

- [ ] **Step 5: Run tests and confirm pass**

Run: `python -m pytest skills/financial-data/tests/test_registry_routing.py -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/financial-data/scripts/registry.py skills/financial-data/scripts/source_health.py skills/financial-data/scripts/routing.py skills/financial-data/references/source-registry.md skills/financial-data/references/source-routing.md skills/financial-data/references/compliance.md skills/financial-data/references/fallback-policy.md skills/financial-data/tests/test_registry_routing.py
git commit -m "feat(financial-data): add source routing and health"
```

---

### Task 4: Normalization, validation, conflict detection, and output profiles

**Files:**
- Create: `skills/financial-data/scripts/normalize.py`
- Create: `skills/financial-data/scripts/validation.py`
- Create: `skills/financial-data/references/data-contract.md`
- Create: `skills/financial-data/references/validation-rules.md`
- Create: `skills/financial-data/references/market-conventions.md`
- Test: `skills/financial-data/tests/test_normalize_validation.py`

**Interfaces:**
- Produces: `normalize_percentage`, `normalize_currency`, `normalize_timestamp`, `validate_point`, `validate_ohlcv`, `compare_points`, `compress_result`.
- `compare_points(a, b, *, rel_tol=0.005, abs_tol=0.0) -> list[QualityFlag]`.

- [ ] **Step 1: Write failing normalization/validation tests**

```python
from skills.financial_data.scripts.normalize import normalize_percentage
from skills.financial_data.scripts.validation import compare_values, validate_ohlcv


def test_percent_normalizes_to_decimal():
    assert normalize_percentage("3.21%") == 0.0321


def test_ohlcv_rejects_invalid_high():
    errors = validate_ohlcv({"open": 10, "high": 9, "low": 8, "close": 9.5, "volume": 100})
    assert "VALIDATION_FAILED" in errors[0]


def test_cross_source_conflict_is_explicit():
    assert compare_values(100.0, 103.0, rel_tol=0.005) is False
```

- [ ] **Step 2: Run and verify failure**

Run: `python -m pytest skills/financial-data/tests/test_normalize_validation.py -q`
Expected: missing modules/functions.

- [ ] **Step 3: Implement normalization**

Handle numeric strings with commas, `%`, `万`, `亿`, `K`, `M`, `B` only when the unit convention is explicit. Do not infer currency from magnitude. ISO timestamps must preserve timezone offset; naive datetime input is rejected unless caller supplies a timezone.

- [ ] **Step 4: Implement validation and conflict policy**

Checks: required provenance, OHLC invariants, non-negative volume/turnover, sorted/unique time series, stale timestamps, unit/currency mismatch, cross-source tolerance. `compare_points` must return a `SOURCE_CONFLICT` quality flag when comparable normalized values exceed tolerance.

- [ ] **Step 5: Implement output profiles**

`compress_result(result, "compact")` retains only current-task fields plus provenance summary; `standard` retains normalized data + quality + sources; `full` preserves diagnostic metadata. Raw provider payload is never included unless explicitly attached by an adapter under debug mode.

- [ ] **Step 6: Run tests and confirm pass**

Run: `python -m pytest skills/financial-data/tests/test_normalize_validation.py -q`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add skills/financial-data/scripts/normalize.py skills/financial-data/scripts/validation.py skills/financial-data/references/data-contract.md skills/financial-data/references/validation-rules.md skills/financial-data/references/market-conventions.md skills/financial-data/tests/test_normalize_validation.py
git commit -m "feat(financial-data): normalize and validate market data"
```

---

### Task 5: Deterministic local derived metrics

**Files:**
- Create: `skills/financial-data/scripts/indicators.py`
- Test: `skills/financial-data/tests/test_indicators.py`

**Interfaces:**
- Produces: `returns`, `sma`, `ema`, `rsi`, `macd`, `bollinger`, `volatility`, `drawdown`, `historical_percentile`, `turnover_rate`, `turnover_concentration`.

- [ ] **Step 1: Write failing deterministic tests**

```python
from skills.financial_data.scripts.indicators import sma, turnover_rate


def test_sma():
    assert sma([1, 2, 3, 4, 5], 3) == [None, None, 2.0, 3.0, 4.0]


def test_turnover_rate_uses_shares_not_value():
    assert turnover_rate(volume_shares=10_000_000, free_float_shares=1_000_000_000) == 0.01
```

Add fixture-based assertions for EMA/RSI/MACD against independently calculated expected values with fixed tolerances.

- [ ] **Step 2: Run and verify failure**

Run: `python -m pytest skills/financial-data/tests/test_indicators.py -q`
Expected: missing indicators module.

- [ ] **Step 3: Implement pure-Python calculations**

No network calls and no provider-specific assumptions. Functions accept plain sequences and return plain lists/numbers. `turnover_rate` requires explicit free-float shares and refuses market-cap proxies. Derived metadata will be added by the facade, not indicator functions.

- [ ] **Step 4: Run tests and confirm pass**

Run: `python -m pytest skills/financial-data/tests/test_indicators.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/financial-data/scripts/indicators.py skills/financial-data/tests/test_indicators.py
git commit -m "feat(financial-data): add deterministic indicators"
```

---

### Task 6: Adapter interface and three stable v0.1.0 adapters

**Files:**
- Create: `skills/financial-data/scripts/adapters/__init__.py`
- Create: `skills/financial-data/scripts/adapters/base.py`
- Create: `skills/financial-data/scripts/adapters/tencent.py`
- Create: `skills/financial-data/scripts/adapters/sec_edgar.py`
- Create: `skills/financial-data/scripts/adapters/treasury.py`
- Create fixtures under `skills/financial-data/tests/fixtures/`
- Extend tests: `skills/financial-data/tests/test_facade.py`

**Interfaces:**
- Produces abstract interface:

```python
class SourceAdapter(Protocol):
    source_id: str
    def supports(self, request: DataRequest, instrument: Instrument) -> bool: ...
    def fetch(self, request: DataRequest, instrument: Instrument) -> list[DataPoint]: ...
```

- Adapter constructors accept injectable `session` and `clock` to make tests deterministic.

- [ ] **Step 1: Write fixture-first adapter tests**

Use fake sessions returning local fixture JSON/text. Assertions:
- Tencent quote parses price/change/turnover with CN instrument provenance.
- SEC companyfacts extracts requested standard metric from XBRL facts while retaining report period/filed date.
- Treasury yield parser returns 2Y/10Y values with date and source provenance.

- [ ] **Step 2: Run and verify failure**

Run: `python -m pytest skills/financial-data/tests/test_facade.py -q`
Expected: missing adapters.

- [ ] **Step 3: Implement shared HTTP helper in base adapter**

Rules: finite timeout (default 8 seconds), at most 2 retries for transient 429/5xx, exponential delay provided through injectable sleeper, descriptive exceptions mapped to `RATE_LIMITED`, `AUTH_REQUIRED`, or `SOURCE_UNAVAILABLE`. No infinite retry.

- [ ] **Step 4: Implement Tencent quote adapter**

Support v0.1.0 fields `quote`, `price`, `turnover`, `market_cap`, `pe`, `pb` for CN equities/indices/ETFs where returned by the endpoint. Keep provider-field mapping isolated inside adapter.

- [ ] **Step 5: Implement SEC EDGAR adapter**

Require caller-provided `SEC_CONTACT` environment variable for network execution; tests inject headers and do not require a real identity. Support `filings` metadata and a small standard metric map: revenue, net_income, operating_cash_flow, assets, liabilities. Preserve XBRL taxonomy tag in metadata.

- [ ] **Step 6: Implement US Treasury adapter**

Support `yield_curve`, `yield_2y`, `yield_10y`, and derived `spread_10y_2y`. Parser must tolerate missing maturities by returning explicit partial-data quality flags instead of fabricating values.

- [ ] **Step 7: Run adapter tests and confirm pass**

Run: `python -m pytest skills/financial-data/tests/test_facade.py -q`
Expected: PASS for fixture tests.

- [ ] **Step 8: Commit**

```bash
git add skills/financial-data/scripts/adapters skills/financial-data/tests/fixtures skills/financial-data/tests/test_facade.py
git commit -m "feat(financial-data): add core source adapters"
```

---

### Task 7: Public facade, fallback orchestration, cross-checks, and workflows

**Files:**
- Create: `skills/financial-data/scripts/financial_data.py`
- Create: `skills/financial-data/scripts/__init__.py`
- Create: `skills/financial-data/references/workflows.md`
- Create: `skills/financial-data/references/a-share.md`
- Create: `skills/financial-data/references/us-hk.md`
- Create: `skills/financial-data/references/macro-rates.md`
- Create: `skills/financial-data/references/futures-commodities.md`
- Create: `skills/financial-data/references/derivatives.md`
- Extend test: `skills/financial-data/tests/test_facade.py`

**Interfaces:**
- Produces primary call:

```python
def get_data(request: DataRequest, *, registry=None, adapters=None) -> DataResult:
    ...
```

- Produces convenience workflows:
`single_stock_snapshot(symbol)`, `peer_comparison(symbols, fields)`, `market_breadth_snapshot(...)`, `macro_snapshot()`, `event_dataset(...)`, `cross_section_fundamentals(...)`.
- Workflows return datasets only; no buy/sell recommendation.

- [ ] **Step 1: Write failing orchestration tests**

Create fake adapters where primary raises `SOURCE_UNAVAILABLE` and backup succeeds. Assert `DataResult.status == "degraded"`, backup source appears in `sources_used`, and `fallbacks_used` records primary -> backup. Add a cross-check test where two adapters disagree beyond tolerance and result contains `SOURCE_CONFLICT` rather than silently suppressing one value.

- [ ] **Step 2: Run and verify failure**

Run: `python -m pytest skills/financial-data/tests/test_facade.py -q`
Expected: missing facade behavior.

- [ ] **Step 3: Implement `get_data` pipeline**

Exact order:
1. Resolve instrument.
2. Route eligible sources.
3. Call primary adapter.
4. On classified failure, record health and move to next independent fallback.
5. Normalize adapter output.
6. Validate.
7. If `require_crosscheck`, call next independent source and compare comparable fields.
8. Attach quality flags and provenance.
9. Compress according to output profile.
10. Return `DataResult`; never return bare `None` or empty list on failure.

- [ ] **Step 4: Implement minimal workflows using `get_data`**

Workflows compose existing fields only. If a requested workflow requires a not-yet-implemented adapter/field, return `FIELD_NOT_SUPPORTED` with the missing field list rather than fake data.

- [ ] **Step 5: Run all core tests**

Run: `python -m pytest skills/financial-data/tests -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/financial-data/scripts/financial_data.py skills/financial-data/scripts/__init__.py skills/financial-data/references/workflows.md skills/financial-data/references/a-share.md skills/financial-data/references/us-hk.md skills/financial-data/references/macro-rates.md skills/financial-data/references/futures-commodities.md skills/financial-data/references/derivatives.md skills/financial-data/tests/test_facade.py
git commit -m "feat(financial-data): orchestrate routing fallback and workflows"
```

---

### Task 8: Agent-facing Skill, README, metadata, attribution, and repository index

**Files:**
- Create: `skills/financial-data/SKILL.md`
- Create: `skills/financial-data/README.md`
- Create: `skills/financial-data/agents/openai.yaml`
- Modify: `README.md`

**Interfaces:**
- Agent Skill instructs when to invoke references/scripts; it does not duplicate endpoint implementation.

- [ ] **Step 1: Write `SKILL.md` frontmatter and activation rules**

Frontmatter:

```yaml
---
name: financial-data
description: 获取、标准化、校验和追踪金融市场数据的统一基础 Skill。用于 A股/港股/美股/指数/ETF/期货/期权/利率/宏观等数据请求，以及需要数据源路由、跨源校验、口径规范、fallback、派生指标或研究数据集准备的任务。
---
```

Main body must stay concise and include:
- Scope and non-goals.
- `Identify -> Route -> Fetch -> Normalize -> Validate -> Cite -> Deliver`.
- Mandatory provenance and time semantics.
- When to read each reference.
- Explicit `SOURCE_CONFLICT` behavior.
- No scraping circumvention.
- Workflow boundary: prepare data, do not substitute for investment research conclusions.

- [ ] **Step 2: Write README examples**

Include exactly practical examples such as:
- 600519 250 trading days + 20/60/120 MA.
- CATL/BYD/EVE Energy valuation comparison.
- AAPL latest 10-Q revenue/net income/OCF with provenance.
- US 2Y/10Y and 10Y-2Y spread.
- A-share industry performance dataset.

Document v0.1.0 implemented adapters separately from registry-only future sources so users do not mistake planned coverage for live capability.

- [ ] **Step 3: Add attribution section**

State that architecture and source-discovery research were informed by Apache-2.0 projects `simonlin1212/a-stock-data` and `simonlin1212/global-stock-data`; do not copy their large embedded implementations verbatim. If any substantive source-derived code is later imported, add source-level copyright/license notices before merge.

- [ ] **Step 4: Add `agents/openai.yaml` following repository convention**

Use a concise display name, description, and default prompt that directs the Agent to use the Skill for source-backed financial data rather than for unsupported investment conclusions.

- [ ] **Step 5: Update root README skill index**

Add `financial-data`: unified financial data access, normalization, validation, routing, and provenance.

- [ ] **Step 6: Commit**

```bash
git add skills/financial-data/SKILL.md skills/financial-data/README.md skills/financial-data/agents/openai.yaml README.md
git commit -m "docs(financial-data): add skill entrypoint and usage"
```

---

### Task 9: Full verification and optional live smoke checks

**Files:**
- Modify only if verification finds concrete defects.

**Interfaces:**
- No new public interfaces.

- [ ] **Step 1: Run repository skill validation**

Run: `python3 scripts/validate_skills.py`
Expected: output includes `Validated 4 skill(s)` (or higher if repository changes concurrently) and exit 0.

- [ ] **Step 2: Run unit/fixture test suite**

Run: `python -m pytest skills/financial-data/tests -q`
Expected: all tests pass.

- [ ] **Step 3: Run syntax/import check**

Run: `python -m compileall skills/financial-data/scripts`
Expected: exit 0.

- [ ] **Step 4: Run optional live smoke tests only when network is available**

Checks:
- Tencent: one CN quote.
- SEC: one AAPL companyfacts/filing call with user-supplied `SEC_CONTACT` only; if absent, verify `AUTH_REQUIRED` instead of inserting an identity.
- Treasury: current/latest yield-curve response.

Live failure is classified as network/upstream vs parser failure; it must not invalidate passing fixture tests without evidence of a code defect.

- [ ] **Step 5: Review diff against design spec**

Verify no raw credential, no giant copied upstream `SKILL.md`, no unsupported capability claimed as implemented, no silent empty-success path, and all documented source priorities match registry behavior.

- [ ] **Step 6: Commit verification fixes if any**

```bash
git add <only-files-changed-by-verification>
git commit -m "fix(financial-data): address verification findings"
```

No commit is needed if verification requires no changes.

## Plan Self-Review

- Spec coverage: Data Contract, Instrument Master, field-level routing, source health, independent fallback, compliance, conflict handling, local derived metrics, Token profiles, workflows, A-share/US/macro/derivatives extension references, tests, and Agent UX are mapped to Tasks 1-9.
- Scope control: only Tencent, SEC EDGAR, and Treasury are mandatory executable adapters for v0.1.0; other sources can be registry/reference entries without pretending execution support.
- Type consistency: all tasks consume the same `DataRequest`, `DataPoint`, `DataResult`, `Instrument`, `SourceSpec`, and `SourceAdapter` interfaces defined earlier.
- No placeholder requirements remain; unsupported v0.1.0 fields must return explicit `FIELD_NOT_SUPPORTED`.
