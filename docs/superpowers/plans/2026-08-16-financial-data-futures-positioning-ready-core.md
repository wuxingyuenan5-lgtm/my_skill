# financial-data Futures Positioning READY Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote official China futures member ranking data into reusable READY helpers with long-form facts, explicit publication status, and deterministic Top-N derived analytics.

**Architecture:** Keep SHFE/INE/DCE/CZCE/CFFEX/GFEX provider parsing isolated, normalize provider rows into one long-form ranking fact schema, then derive Top5/10/20 metrics in a provider-agnostic analytics layer. Empty data is not automatically failure: fetch results carry publication status so threshold-based non-publication can be distinguished from source failure.

**Tech Stack:** Python 3.9+, stdlib (`csv`, `io`, `re`, `datetime`, XML/ZIP), existing `HttpClient`, pytest deterministic fixtures/fakes, Markdown/YAML capability documentation.

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

## Execution status

- [x] Canonical long-form ranking fact, validation and publication-status result contract.
- [x] SHFE current structured ranking parser/fetcher.
- [x] INE structured parser; transport intentionally remains RECIPE because the current machine path is not frozen through the observed WAF.
- [x] DCE official batch ZIP parser/fetcher.
- [x] GFEX contract discovery + three independent ranking-page parser/fetcher.
- [x] CFFEX product CSV parser/fetcher.
- [x] CZCE current XLSX parser/fetcher with explicit `2025-11-02+` READY boundary.
- [x] Top5/10/20 sums, changes, disclosed-subset `long_minus_short`, and denominator-safe concentration.
- [x] Dispatcher/public exports and v0.2.2 daily-row denominator bridge.
- [x] Capability Index v6 and handbook/README synchronization.
- [x] Draft PR #1 refresh; branch remains unmerged.

## READY status

- **READY:** SHFE / DCE / CZCE / CFFEX / GFEX member rankings.
- **RECIPE / parser-ready:** INE member rankings.
- **RECIPE umbrella:** `cn_futures_member_positions` remains RECIPE until INE transport is independently frozen.
- **READY derived analytics:** `aggregate_top_n` / `aggregate_standard_windows`.

## Fresh verification

- Positioning deterministic suite: **10 passed**.
- Shared GET/POST/binary HTTP transport regression: **3 passed**.
- Python 3.9 AST + compile checks passed for the positioning and changed HTTP modules.
- Five READY exchange fetchers plus Top-N runtime imported/callable in the deterministic workspace; INE parser callable and intentionally absent from READY dispatcher.
- Feature-vs-main compare performed; this phase wrote only to `feat/financial-data-skill`.

## Verification limitation

The execution environment still does not provide a complete local Git checkout because container-side GitHub DNS resolution is unavailable. Therefore this phase does **not** claim a fresh full-repository pytest run or a live endpoint availability guarantee. Focused deterministic tests exercise parser/fetch-routing contracts with representative fixtures/fake transports. Downstream production projects should maintain timestamped live smoke checks and `last_verified` state.
