# financial-data Encyclopedia Navigation Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reframe `financial-data` as a token-efficient financial-data acquisition encyclopedia that routes narrow requests to the smallest relevant task/dataset/provider cards and makes provider/API constraints explicit.

**Architecture:** `SKILL.md` becomes the operating contract and points to a compact `NAVIGATION.md`. `NAVIGATION.md` routes to one task card, dataset card, or provider card; task cards identify required datasets, dataset cards shortlist sources, and provider cards contain standardized source constraints plus copy guidance. Existing `references/` and `scripts/financial_data/` remain detailed references and verified copy-ready implementations rather than default reading or downstream runtime dependencies.

**Tech Stack:** Markdown, existing repository references/runtime, lightweight pytest/static path checks, current official provider documentation for volatile access/rate/history/licensing facts.

## Global Constraints

- Work only on `feat/financial-data-skill`; do not merge or force-rewrite `main`.
- Target documentation version is **v0.3 encyclopedia-first**.
- Do not build a new data service, API server, database, orchestration layer, runtime router, or schema engine.
- Do not require downstream projects to import or call the Skill after the selected source rules/code are frozen locally.
- `references/capability-index.yaml` remains maintenance/audit metadata and must not be the ordinary first-read document.
- Normal narrow lookups should usually finish within `SKILL.md + NAVIGATION.md + 1-3 relevant cards` and no more than roughly 3-5 small files total.
- Provider cards must separate official limits from conservative/empirical recommendations. Unknown current facts must be recorded as `unknown` / `provider_not_committed`, never guessed.
- Exact current provider limits/auth/history/licensing facts must be verified from current official/provider sources when available; unstable facts should record `last_verified`.
- Never include CAPTCHA/WAF/access-control bypass instructions.
- Existing runtime modules are retained as verified reference implementations and copy-ready utilities; do not delete them merely to make the Skill more document-centric.

---

### Task 1: Lock the lightweight navigation contract with failing static tests

**Files:**
- Create: `skills/financial-data/tests/test_encyclopedia_navigation.py`
- Later consumed by: all files created in Tasks 2-5

**Interfaces:**
- Consumes: filesystem layout under `skills/financial-data/`.
- Produces: static assertions for default-entry wording, first-pass route targets, mandatory provider-card sections, and absence of unresolved placeholders.

- [ ] **Step 1: Write failing tests for the v0.3 contract**

Create tests that assert:

```python
ROOT = Path(__file__).resolve().parents[1]

PROVIDER_SECTIONS = [
    "## Identity",
    "## Access and authentication",
    "## Technical request limits",
    "## Data-range limits",
    "## Freshness and publication timing",
    "## Licensing and redistribution",
    "## Data-quality limitations",
    "## Copy guidance",
]
```

The tests must check that:

1. `SKILL.md` points to `NAVIGATION.md` and does not instruct ordinary lookups to search the full capability index first.
2. `NAVIGATION.md` exists.
3. Every first-pass target listed in `NAVIGATION.md` exists.
4. Every file in `providers/*.md` contains all `PROVIDER_SECTIONS` plus `last_verified`.
5. No new `NAVIGATION.md`, task, dataset, or provider card contains `TBD` or `TODO`.
6. README contains both `v0.3 encyclopedia-first` and the downstream-runtime-independence statement.

- [ ] **Step 2: Run the focused test and confirm RED**

Run:

```bash
pytest skills/financial-data/tests/test_encyclopedia_navigation.py -q
```

Expected: FAIL because `NAVIGATION.md` and the new cards do not yet exist and `SKILL.md` still says to search the capability index first.

- [ ] **Step 3: Commit only the failing contract test**

```bash
git add skills/financial-data/tests/test_encyclopedia_navigation.py
git commit -m "test: define encyclopedia navigation contract"
```

---

### Task 2: Create the compact default navigation and task cards

**Files:**
- Create: `skills/financial-data/NAVIGATION.md`
- Create: `skills/financial-data/tasks/a-share-ma-strategy.md`
- Create: `skills/financial-data/tasks/a-share-market-breadth.md`
- Create: `skills/financial-data/tasks/futures-term-structure.md`
- Create: `skills/financial-data/tasks/futures-positioning.md`
- Create: `skills/financial-data/tasks/lithium-carbonate-research.md`
- Create: `skills/financial-data/tasks/copper-research.md`
- Create: `skills/financial-data/tasks/cross-asset-research.md`
- Create: `skills/financial-data/tasks/us-equity-fundamentals.md`

**Interfaces:**
- Consumes: existing detailed references such as `references/a-share-market-data.md`, `references/futures-ready-core.md`, `references/futures-positioning-ready-core.md`, `references/global-equity-fundamentals.md`.
- Produces: first-hop progressive-disclosure routes and research-task dataset shortlists.

- [ ] **Step 1: Create a compact `NAVIGATION.md`**

It must contain four routing sections:

```text
Research task -> one tasks/*.md
Concrete dataset -> one datasets/**/*.md
Named provider/API -> one providers/*.md
Maintenance/audit -> references/capability-index.yaml
```

Include the complete first-pass routes from the approved spec and state the default read budget explicitly:

```text
Do not scan the full Skill by default.
Start with this file, open one first-hop card, then only shortlisted provider cards.
A normal narrow lookup should usually stay within 3-5 small files total.
```

- [ ] **Step 2: Create all eight task cards**

Every task card must contain:

```text
## Objective
## Required datasets
## Optional datasets
## Recommended source path
## Methodology / caveats
## What to freeze into the downstream project
## Avoid unnecessary reads
```

Task cards link primarily to dataset cards and only directly to providers when the provider is intrinsic to the task.

- [ ] **Step 3: Run the focused navigation test**

Run:

```bash
pytest skills/financial-data/tests/test_encyclopedia_navigation.py -q
```

Expected: still FAIL because dataset/provider cards and SKILL/README changes are not complete, but navigation-target failures for the task-card section should be gone.

- [ ] **Step 4: Commit navigation + task cards**

```bash
git add skills/financial-data/NAVIGATION.md skills/financial-data/tasks
git commit -m "docs: add task-first financial data navigation"
```

---

### Task 3: Create dataset encyclopedia cards

**Files:**
- Create: `skills/financial-data/datasets/cn-equity/kline.md`
- Create: `skills/financial-data/datasets/cn-equity/market-cross-section.md`
- Create: `skills/financial-data/datasets/cn-equity/industry-classification.md`
- Create: `skills/financial-data/datasets/futures/daily-contract-market-data.md`
- Create: `skills/financial-data/datasets/futures/member-position-ranking.md`
- Create: `skills/financial-data/datasets/futures/warehouse-inventory.md`
- Create: `skills/financial-data/datasets/futures/trading-parameters.md`
- Create: `skills/financial-data/datasets/global-equity/kline.md`
- Create: `skills/financial-data/datasets/global-equity/sec-filings-companyfacts.md`
- Create: `skills/financial-data/datasets/macro/us-rates-treasury.md`
- Create: `skills/financial-data/datasets/macro/cftc-positioning.md`
- Create: `skills/financial-data/datasets/crypto/exchange-market-data.md`

**Interfaces:**
- Consumes: task-card requirements and existing detailed reference pages/runtime names.
- Produces: canonical dataset definitions and source shortlists that point to provider cards.

- [ ] **Step 1: Create the twelve dataset cards**

Every dataset card must contain:

```text
## What this dataset means
## Common analytical uses
## Minimum canonical fields
## Frequency and timing semantics
## Recommended sources
## Alternatives / licensed alternatives
## Methodology and unit caveats
## Source-selection pitfalls
## Provider cards
## Copy-ready references
```

Do not duplicate full provider rate-limit/auth details here; link to provider cards instead.

- [ ] **Step 2: Preserve critical semantics in dataset cards**

At minimum:

- CN equity K-line: adjustment, volume/amount units, suspension/missing-bar handling.
- Industry classification: taxonomy/version/effective-date/PIT membership.
- Futures daily: exact vs dominant vs continuous, settlement vs close, night-session trading day.
- Futures positions: volume/long/short are independent ranking lists; Top-N imbalance is not full-market net position.
- Warehouse/inventory: exchange warehouse receipts are not identical to social/physical inventory.
- Futures trading parameters: exchange vs broker margin/fees and date-effective rules.
- SEC/companyfacts: filing/publish/available dates and amendment/revision semantics.
- CFTC: report date vs publication date and category definitions.
- Crypto: exchange/market/symbol and spot-vs-perpetual separation.

- [ ] **Step 3: Run the focused test**

```bash
pytest skills/financial-data/tests/test_encyclopedia_navigation.py -q
```

Expected: dataset route-target checks pass; provider/SKILL/README checks still fail until later tasks.

- [ ] **Step 4: Commit dataset cards**

```bash
git add skills/financial-data/datasets
git commit -m "docs: add financial dataset encyclopedia cards"
```

---

### Task 4: Create standardized provider cards with verified constraint provenance

**Files:**
- Create: `skills/financial-data/providers/tencent.md`
- Create: `skills/financial-data/providers/eastmoney.md`
- Create: `skills/financial-data/providers/sina.md`
- Create: `skills/financial-data/providers/cninfo.md`
- Create: `skills/financial-data/providers/shfe.md`
- Create: `skills/financial-data/providers/ine.md`
- Create: `skills/financial-data/providers/dce.md`
- Create: `skills/financial-data/providers/czce.md`
- Create: `skills/financial-data/providers/cffex.md`
- Create: `skills/financial-data/providers/gfex.md`
- Create: `skills/financial-data/providers/yahoo.md`
- Create: `skills/financial-data/providers/sec-edgar.md`
- Create: `skills/financial-data/providers/us-treasury.md`
- Create: `skills/financial-data/providers/cftc.md`
- Create: `skills/financial-data/providers/binance.md`
- Create: `skills/financial-data/providers/wind-choice.md`
- Create: `skills/financial-data/providers/tradingview.md`

**Interfaces:**
- Consumes: current official/provider documentation where available, existing repository provider notes, and current verified reference implementations.
- Produces: one standardized Source Constraint Card per provider.

- [ ] **Step 1: Verify volatile provider constraints before writing exact claims**

For each provider, use current official/provider documentation when it exposes access limits, auth, history caps, timing, or licensing terms. Record exact values only when verified. Otherwise write explicit values such as:

```text
official_rate_limit: unknown
recommended_operating_limit: empirical; see notes
historical_limit: endpoint-dependent / unknown
last_verified: 2026-08-16
```

Never turn an empirical recommendation into an official limit.

- [ ] **Step 2: Create all seventeen provider cards**

Every provider card must contain exactly these required second-level sections:

```text
## Identity
## Access and authentication
## Technical request limits
## Data-range limits
## Freshness and publication timing
## Licensing and redistribution
## Data-quality limitations
## Copy guidance
```

Each card must also state `last_verified` near the top and distinguish source-of-record vs vendor-derived data.

- [ ] **Step 3: Preserve provider-specific constraints**

At minimum capture:

- public vendor sources (Tencent/Eastmoney/Sina/Yahoo): endpoint families, unofficial/public-web nature where applicable, blocking/rate-limit uncertainty, and research-vs-redistribution caveats;
- CNINFO/exchanges: official-source status, publication timing/format regimes where known, and WAF/CAPTCHA/access-control notes without bypass instructions;
- INE: current positioning-machine-path remains unfrozen; official page availability does not equal READY machine transport;
- SEC EDGAR: truthful User-Agent and published fair-access guidance;
- Treasury/CFTC: official public-data nature and relevant update/report timing;
- Binance: official market-data API limits/auth semantics only if current official docs verify them; regional/account restrictions stay explicit;
- Wind/Choice: licensed-terminal/API entitlement and redistribution restrictions; do not invent public API quotas;
- TradingView: distinguish Widgets, Advanced Charts/Datafeed, Lightweight Charts, Pine, and market-data licensing; do not present it as a generic scraping API.

- [ ] **Step 4: Run provider-card contract test**

```bash
pytest skills/financial-data/tests/test_encyclopedia_navigation.py -q
```

Expected: provider-section and route-target assertions pass; remaining failures should be limited to SKILL/README wording if not yet changed.

- [ ] **Step 5: Commit provider cards**

```bash
git add skills/financial-data/providers
git commit -m "docs: add provider API constraint encyclopedia"
```

---

### Task 5: Reframe SKILL.md and README around encyclopedia-first progressive disclosure

**Files:**
- Modify: `skills/financial-data/SKILL.md`
- Modify: `skills/financial-data/README.md`

**Interfaces:**
- Consumes: `NAVIGATION.md`, task/dataset/provider cards, existing runtime/reference layout.
- Produces: default behavior that prevents broad scans and makes downstream independence explicit.

- [ ] **Step 1: Replace the current capability-index-first startup instructions in `SKILL.md`**

The opening operating contract must say:

```text
Default: read NAVIGATION.md first.
Classify the request as research-task, concrete-dataset, named-provider, or maintenance/audit.
Do not read the full capability index or enumerate all providers for a narrow request.
Open one first-hop card, then only shortlisted provider/reference files.
Normal lookup budget: roughly 3-5 small files.
```

Keep global correctness rules (identity, units, provenance, settlement, PIT, licensing) but remove language that makes shared runtime the conceptual center.

- [ ] **Step 2: Update README to v0.3 encyclopedia-first**

README must state:

```text
Shared runtime exists as verified reference implementations and copy-ready utilities.
Downstream projects are not expected to depend on this Skill at runtime after selected source logic has been frozen into the project.
```

Move navigation instructions ahead of runtime examples. Keep runtime examples as optional reference-implementation examples.

- [ ] **Step 3: Run the focused test and confirm GREEN**

```bash
pytest skills/financial-data/tests/test_encyclopedia_navigation.py -q
```

Expected: all tests in this file PASS.

- [ ] **Step 4: Run relevant existing documentation/skill-contract tests**

```bash
pytest skills/financial-data/tests/test_skill_contract.py skills/financial-data/tests/test_python_compat.py -q
```

Expected: PASS; if existing assertions conflict with the approved v0.3 identity, update only assertions that encode the old capability-index-first/runtime-first wording.

- [ ] **Step 5: Commit SKILL/README changes**

```bash
git add skills/financial-data/SKILL.md skills/financial-data/README.md skills/financial-data/tests
git commit -m "docs: make financial-data encyclopedia-first"
```

---

### Task 6: Final route audit, scenario validation, and Draft PR refresh

**Files:**
- Modify if required by validation: files from Tasks 2-5
- Modify: Draft PR #1 body

**Interfaces:**
- Consumes: completed v0.3 documentation tree.
- Produces: evidence that narrow queries resolve without broad scans and that PR documentation matches actual status.

- [ ] **Step 1: Run fresh deterministic verification**

Run:

```bash
pytest skills/financial-data/tests/test_encyclopedia_navigation.py skills/financial-data/tests/test_skill_contract.py skills/financial-data/tests/test_python_compat.py -q
```

Also scan new navigation/card files for placeholders and broken local links using a small one-off stdlib Python check; no new runtime framework is needed.

- [ ] **Step 2: Validate the four representative navigation scenarios manually/staticly**

Verify these exact paths:

```text
A股日K做均线策略
-> SKILL.md -> NAVIGATION.md -> tasks/a-share-ma-strategy.md
-> datasets/cn-equity/kline.md -> providers/tencent.md (and only shortlisted alternatives if needed)

碳酸锂期货持仓排名
-> SKILL.md -> NAVIGATION.md
-> datasets/futures/member-position-ranking.md -> providers/gfex.md

东财接口有什么限制
-> SKILL.md -> NAVIGATION.md -> providers/eastmoney.md

整个Skill有哪些READY能力
-> SKILL.md -> NAVIGATION.md -> references/capability-index.yaml
```

Ordinary narrow scenarios must not require a full capability-index scan.

- [ ] **Step 3: Check branch/PR state**

Confirm feature branch is still `feat/financial-data-skill`, PR #1 remains Draft/open/not merged, and no `main` write occurred in this phase.

- [ ] **Step 4: Refresh PR #1 body**

Add a concise v0.3 section describing:

- encyclopedia-first navigation;
- 3-5-file progressive-disclosure budget;
- task/dataset/provider cards;
- standardized API/source constraints and `last_verified` policy;
- capability index demotion to maintenance/audit;
- runtime retained only as verified reference/copy-ready implementation;
- fresh focused validation evidence and any explicit current limitations.

- [ ] **Step 5: Do not merge**

Leave the Draft PR open for later review/integration. No merge or force rewrite is part of this plan.
