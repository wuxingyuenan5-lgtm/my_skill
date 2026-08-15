# financial-data Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `skills/financial-data` v0.1.0 as a reusable financial-data foundation that identifies instruments, routes requests to appropriate sources, normalizes and validates results with provenance, supports independent fallback, computes deterministic derived metrics locally, and exposes a concise Agent-facing Skill.

**Architecture:** Keep `SKILL.md` thin and declarative. Put long market/source rules in `references/`; reusable Python logic in focused modules under `scripts/financial_data/`; adapters behind a common `SourceAdapter` interface; tests use fixtures by default and a small optional live-smoke layer. The public Python facade composes instrument resolution, routing, adapter execution, normalization, validation, output compression, and explicit error reporting.

**Tech Stack:** Python 3.9+ standard library + `requests`; `pytest` for tests. No required pandas/akshare/mootdx dependency in v0.1.0.

## Global Constraints

- Skill directory: `skills/financial-data/`; frontmatter `name` equals `financial-data`.
- Initial version: `0.1.0`.
- Core flow: `Identify -> Route -> Fetch -> Normalize -> Validate -> Cite -> Deliver`.
- Percentages are decimals internally.
- Every successful standardized datum carries provenance, `as_of`, and `retrieved_at`.
- Distinguish `trade_date`, `calendar_date`, `report_period`, `publish_date`, `as_of`, and `retrieved_at`.
- Routing is field-level, not source-global.
- Independent-domain fallback is preferred.
- Source conflicts surface as `SOURCE_CONFLICT`.
- No hard-coded credentials or SEC contact identity.
- No bypass of CAPTCHA/access controls/explicit anti-bot restrictions.
- Deterministic derived metrics are local.

## Implemented Tasks

- [x] Core contracts and explicit error model: `scripts/financial_data/contracts.py`
- [x] Instrument Master and canonical identifiers: `scripts/financial_data/instruments.py`
- [x] Source registry, health, compliance metadata and field-level routing
- [x] Normalization, validation, conflict detection and output profiles
- [x] Deterministic local indicators: returns/SMA/EMA/RSI/MACD/Bollinger/volatility/drawdown/KDJ/turnover/breadth
- [x] Adapter interface + Tencent CN quote + Sina independent fallback + SEC EDGAR + US Treasury
- [x] Public facade with fallback orchestration, cross-checks and data workflows
- [x] Agent-facing `SKILL.md`, README, references, OpenAI metadata and root repo index
- [x] Python 3.9 compatibility guard
- [x] Fixture-based adapter tests and orchestration tests
- [x] Repository skill validation, compile/import verification

## Verification Record

Executed against the implementation tree on 2026-08-15:

```text
python -m pytest skills/financial-data/tests -q
60 passed

python3 scripts/validate_skills.py
Validated 4 skill(s)

python -m compileall -q skills/financial-data/scripts/financial_data
exit 0

PYTHONPATH=skills/financial-data/scripts python -c 'import financial_data'
import successful
```

Live Internet smoke tests could not run in the local execution container because outbound DNS/GitHub/public-web resolution was unavailable. Provider parsers are therefore covered by deterministic fixtures, while live source reachability remains a deployment-time check.

## Deliberately Deferred Beyond v0.1.0

These are represented in the registry/references but are not claimed as executable adapters:

- Eastmoney exclusive A-share endpoints (fund flow, margin, block trades, shareholder count, limit-state, sectors)
- CNINFO/SSE/SZSE filing/official-market adapters
- CFTC COT
- Yahoo quote/K-line/options
- CBOE options/Greeks/0DTE
- FINRA short volume
- SEC Frames cross-sectional screener
- production K-line adapters / market-wide sector datasets

Each should enter a future minor release only with source-specific fixtures, normalization tests, routing rules, and compliance review.
