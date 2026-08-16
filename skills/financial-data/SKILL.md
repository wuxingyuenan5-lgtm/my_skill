---
name: financial-data
description: Use when a task needs to identify, compare, or copy financial-data sources and retrieval recipes across equities, futures, options, funds, rates, macro, FX, crypto, filings, or chart integrations.
---

# financial-data

## Identity

This Skill is a **financial-data acquisition encyclopedia**: a source map, dataset handbook, provider-constraint reference, methodology guide, and library of verified copy-ready implementations.

Its normal lifecycle is:

**consult the Skill → shortlist the needed dataset/source → copy/freeze the selected recipe and rules into the downstream project → the downstream project owns recurring updates.**

Shared runtime exists as verified reference implementations and copy-ready utilities. Downstream projects are not expected to depend on this Skill at runtime after the selected source logic has been frozen into the project.

## Default navigation — progressive disclosure

**Read `NAVIGATION.md` first.** Classify the request before opening detailed files:

1. research task → open one `tasks/*.md` card;
2. concrete dataset → open one `datasets/**/*.md` card;
3. named provider/API → open that one `providers/*.md` card directly;
4. maintenance/coverage audit → only then use `references/capability-index.yaml`.

### Read budget

- **Do not read the full capability index for an ordinary narrow request.**
- Do not enumerate all providers before shortlisting.
- Do not scan every domain reference page to answer one dataset question.
- Open one first-hop card first, then only shortlisted provider/reference files.
- A normal narrow lookup should usually stay within **3-5 small files total**.
- Expand one level at a time only when the first route is insufficient.

The full capability index is maintenance metadata, not the default search surface.

## Three encyclopedia layers

### 1. Task cards — “what data do I need?”

`tasks/` maps a research question to the minimum required/optional datasets, recommended source path, methodology caveats, and what to freeze into the project.

### 2. Dataset cards — “what exactly is this data and which sources fit?”

`datasets/` defines canonical meaning, minimum fields, frequency/timing, source shortlist, units/methodology, pitfalls, and links to provider cards/reference implementations.

### 3. Provider cards — “how can I use this source safely?”

`providers/` records source identity plus access/auth, technical limits, history/range, publication timing, licensing, quality limitations, and copy guidance.

Provider cards must distinguish:

- **officially published limits** from empirical/recommended operating limits;
- source-of-record facts from vendor-derived/estimated/editorial data;
- public web accessibility from commercial redistribution rights;
- legitimate no-data/non-publication states from source failures.

If a current rate limit, history cap, authentication rule, or right cannot be verified, write `unknown` / `provider_not_committed`; never invent a number. Preserve `last_verified` for volatile source constraints when practical.

## Core data-correctness rules

1. Resolve canonical instrument identity before provider aliases; never guess ambiguous symbols.
2. Route by **asset class + market + dataset + intended usage**, not one global favorite provider.
3. Keep official facts, vendor-derived values, estimates/editorial tags, and local calculations as separate data classes.
4. Preserve provenance plus `as_of`, `retrieved_at`, currency/unit, and relevant trade/report/publish/available dates.
5. Percentages are decimals internally; declare price adjustment, volume/turnover units, futures multiplier, and settlement-vs-close semantics.
6. Important vendor-derived data should use an independent cross-check when practical; surface source conflicts instead of silently choosing one value.
7. Provider failure is not equivalent to “no data.”
8. Preserve field-map corrections, stale-symbol warnings, historical endpoint regimes and other quirks that prevent silent errors.
9. Never bypass CAPTCHA, WAF challenges, access controls, or explicit anti-bot restrictions.
10. Re-check current data rights before commercial use or redistribution.
11. Prefer deterministic local calculation for indicators, returns, dominant/continuous futures, term structure, basis and other derived metrics; record methodology.
12. Point-in-time research must use information that was actually available at the historical decision time.

## Existing detailed references

The older `references/` handbook remains valuable for deeper detail. Reach it **through a task/dataset/provider card** whenever possible rather than loading it broadly.

Key maintenance/deep-reference groups include:

- A-shares: `references/a-share-*.md`
- global equities/SEC: `references/global-equity-*.md`, `references/sec-edgar-advanced.md`
- futures: `references/futures-*.md`
- macro/rates/CFTC: `references/macro-*.md`
- TradingView/chart integration: `references/tradingview*.md`, `references/chart-data-contract.md`
- source quality/licensing/routing: `references/source-*.md`, `references/fallback-policy.md`, `references/compliance.md`
- project extraction: `references/project-export.md`

## Verified reference implementations

`scripts/financial_data/` contains tested examples for selected sources and transformations, including Tencent, Yahoo, Eastmoney, SEC, Treasury, CFTC, China futures daily/positioning, chart transforms and futures analytics.

Use them as **reference/copy material**, not as a required long-lived dependency. A downstream project may simplify, rename, adapt or replace them once it has frozen the required semantics and tests locally.

## Futures invariant

Exact contracts, dominant contracts and continuous series are different instruments. Preserve exchange trading day for night sessions, settlement separately from close, contract multiplier/unit, expiry and explicit roll/adjustment methodology. Member volume/long/short rankings are disclosure subsets and independent ranking lists, not full-market net positions.

## TradingView invariant

Do not call everything a “TradingView API.” Widgets use TradingView-supplied symbols; Advanced Charts/Trading Platform require a project/third-party datafeed and do not themselves provide market data; Lightweight Charts renders project data; Pine is a separate scripting environment. TradingView is primarily a visualization/integration layer here, not an unofficial generic data scraper.

## Maintenance / audit mode

Only when the user asks for whole-Skill coverage, READY/RECIPE/RESTRICTED inventory, migration status, or maintenance should you open `references/capability-index.yaml`, `references/capability-schema.md`, or `references/reference-repo-coverage.md` broadly.
