# financial-data Futures Positioning READY Core Design

## Context

`financial-data` v0.2.2 already provides official daily contract OHLC/settlement READY helpers for SHFE, INE, DCE, CZCE, CFFEX and GFEX, plus local dominant-contract and term-structure analytics. The next approved batch is **v0.2.3 Futures Positioning READY Core**.

The existing handbook documents member rankings only at a high level. This phase turns exchange-published volume/long/short member rankings into a reusable official-source layer while preserving an important market-structure fact: ranking disclosures are not necessarily published for every contract every day. Therefore an empty result cannot automatically mean source failure.

## Goal

Provide reusable official-source helpers for China futures member rankings and deterministic derived top-N analytics:

- volume ranking;
- long-open-interest ranking;
- short-open-interest ranking;
- daily change for each ranking value;
- top 5 / 10 / 20 sums;
- top-N long-minus-short derived indicator;
- top-N concentration when a valid market denominator is explicitly supplied.

The output must be usable directly by commodity/financial-futures research projects without pretending that exchange ranking tables represent the full market or a member's proprietary directional view.

## Scope

### In scope

1. SHFE, INE, DCE, CZCE, CFFEX and GFEX official member-ranking source families.
2. Exchange-specific fetch/parser functions where current machine transport can be frozen; parser/recipe-only status otherwise.
3. One long-form canonical ranking fact schema.
4. Explicit publication status semantics.
5. Member-name preservation and conservative normalization.
6. Top-N derived aggregation helpers.
7. Capability Index and handbook updates.
8. Deterministic fixtures/tests and optional timestamped live smoke checks.

### Out of scope

- warehouse receipts and inventory;
- margin/limit/fee/trading-parameter snapshots;
- delivery statistics;
- CTP or licensed intraday feeds;
- attempts to infer proprietary-vs-client positions from exchange ranking tables.

## Canonical long-form fact

```python
{
    "trade_date": "2026-08-14",
    "exchange": "SHFE",
    "scope_type": "contract",
    "scope_id": "CU2609",
    "variety": "CU",
    "contract_id": "CU2609",
    "ranking_type": "long",
    "rank": 1,
    "member": "某期货",
    "value": 12345,
    "change": -321,
    "source_id": "shfe",
    "source_url": "...",
    "raw": {...},
}
```

`ranking_type` is one of `volume`, `long`, `short`.

The internal model does **not** align three independent ranking lists by rank number. Wide output is a presentation/export convenience only.

## Publication status

The result envelope distinguishes:

- `published`;
- `not_published_by_rule`;
- `no_trading`;
- `source_failure`.

A provider error/WAF page never becomes a successful empty result. Where a valid empty payload cannot prove the precise cause, metadata records that the non-publication status is inferred.

## Derived analytics

For one exchange/trade-date/scope:

```text
TopN volume = sum(volume-ranking values where rank <= N)
TopN long   = sum(long-ranking values where rank <= N)
TopN short  = sum(short-ranking values where rank <= N)
TopN imbalance = TopN long - TopN short
```

This imbalance is a **disclosed-subset derived indicator**, not full-market net positioning.

Concentration is calculated only with an explicit matching denominator:

```text
volume concentration = TopN volume / exact-contract daily volume
long concentration   = TopN long / exact-contract daily open interest
short concentration  = TopN short / exact-contract daily open interest
```

No denominator => no concentration estimate.

## Exchange isolation

Each exchange keeps provider-specific request/parsing logic separate. Shared code begins only at canonical fact creation and derived analytics.

### SHFE

Use the current structured Daily Ranking family with `o_cursor` rows and participant/volume/long/short fields. The current machine family can be frozen as READY.

### INE

The official Daily Ranking page and ranking disclosure semantics are documented, but current automated access can trigger WAF/human verification. The SHFE-style structured parser may exist independently; the exchange capability remains RECIPE/parser-ready until a current machine fetch route is independently frozen and tested. Do not guess from historical SHFE-like paths.

### DCE

Use the current official member-position batch-download family and parse per-contract ranking files into three independent ranking lists.

### CZCE

Use the current XLSX holding-report regime for READY support. Older XLS/HTML/text regimes are documented separately and must not be silently guessed by the current fetcher.

### CFFEX

Use the current product CSV ranking family. Product-level request selection is explicit (e.g. IF/IC/IM/IH/T/TF/TS/TL); exchange disclosure rules mean missing data is not automatically a source failure.

### GFEX

Use the official variety/contract discovery and member-position request families. `data_type=1/2/3` are treated as independent ranking lists.

## Capability model

The umbrella capability remains RECIPE unless all six exchange transports satisfy READY rules. Partial readiness is represented explicitly with exchange-level entries.

READY requires:

1. real runtime function;
2. deterministic parser/fetch-routing tests;
3. source/business error semantics;
4. published/not-published handling;
5. documented current source family and coverage boundary.

## Final v0.2.3 outcome

- READY: SHFE, DCE, CZCE, CFFEX, GFEX positioning fetchers.
- RECIPE/parser-ready: INE positioning.
- READY: Top-N positioning analytics and daily-row denominator bridge.
- Umbrella `cn_futures_member_positions`: remains RECIPE until INE transport is frozen.

This partial READY outcome is intentional and conforms to the design requirement that missing current transport evidence must not be promoted.

## Verification

Deterministic tests cover long-form fact semantics, provider parsers, five READY fetch routes with fake transports, INE explicit non-READY routing, Top-N arithmetic and denominator rules. Python 3.9 compatibility is checked on changed modules. Live endpoint availability remains a separate timestamped smoke layer, not part of the permanent READY guarantee.

## Branch safety

All changes stay on `feat/financial-data-skill` / Draft PR #1. No merge or force rewrite of `main`.
