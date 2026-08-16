# financial-data Futures Positioning READY Core Design

## Context

`financial-data` v0.2.2 already provides official daily contract OHLC/settlement READY helpers for SHFE, INE, DCE, CZCE, CFFEX and GFEX, plus local dominant-contract and term-structure analytics. The next approved batch is **v0.2.3 Futures Positioning READY Core**.

The existing handbook documents member rankings only at a high level. This phase turns exchange-published volume/long/short member rankings into a reusable official-source layer while preserving an important market-structure fact: ranking disclosures are not necessarily published for every contract every day. For example, SHFE/INE and CFFEX apply publication thresholds/rules. Therefore an empty result cannot automatically mean source failure.

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
2. Exchange-specific fetch/parser functions.
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
- CTP/intraday feeds;
- inferred client positioning behind a futures-company member;
- proprietary-vs-client decomposition where the exchange does not disclose it;
- cross-member entity resolution beyond explicit alias maps.

These remain later READY batches.

## Approaches considered

### Option A — Aggregates only

Store only top5/top10/top20 totals.

Pros: compact and easy to consume.  
Cons: destroys member-level facts, prevents seat tracking, cannot re-aggregate with different cutoffs, and hides ranking changes.

### Option B — Wide rank row

One rank row contains volume member/value, long member/value and short member/value side by side.

Pros: resembles many exchange pages and older wrappers.  
Cons: the three ranking lists are independent; rank 1 volume member does not semantically belong to rank 1 long member. Wide rows encourage false joins and are awkward for time-series member research.

### Option C — Long-form fact rows + derived aggregates **(selected)**

Each row represents exactly one ranking fact. Top-N summaries are derived separately.

Pros: preserves exchange facts, supports member tracking and arbitrary top-N calculations, avoids false joins, and isolates derived metrics from raw disclosure.  
Cons: more rows, which is acceptable for this handbook/data-engineering Skill.

## Canonical ranking fact

Each ranking record normalizes to:

```python
{
    "trade_date": "2026-08-14",
    "exchange": "GFEX",
    "scope_type": "contract",        # contract | product
    "scope_id": "LC2609",
    "variety": "LC",
    "contract_id": "LC2609",        # optional when scope_type=product
    "ranking_type": "long",          # volume | long | short
    "rank": 1,
    "member_name": "示例期货",
    "member_name_normalized": "示例期货",
    "value": 12345,
    "change": 321,
    "unit": "contracts",
    "source_id": "gfex",
    "source_url": "...",
    "raw": {...},
}
```

### Required semantics

- `ranking_type=volume` means ranked member trading volume, not open interest.
- `ranking_type=long` means exchange-published buy/long open interest.
- `ranking_type=short` means exchange-published sell/short open interest.
- `change` is the exchange-published change versus the prior trading day where available; it must not be recomputed silently from incomplete local history.
- `rank` is the rank inside its own ranking list.
- `scope_type` is explicit because exchanges may publish rankings by exact contract or by product/aggregate scope.
- `member_name` preserves exact source text. `member_name_normalized` may remove harmless whitespace/full-width differences but must not merge legal entities without an explicit alias map.

## Publication status envelope

Fetchers return an envelope rather than using `[]` for every non-data case:

```python
{
    "status": "published",  # published | not_published_by_rule | no_trading | source_failure
    "exchange": "SHFE",
    "trade_date": "2026-08-14",
    "scope": {...},
    "rows": [...],
    "metadata": {...},
}
```

### Status rules

- `published`: the exchange published a valid ranking table; `rows` may then be parsed.
- `not_published_by_rule`: the exchange page/source is valid, but the requested contract/product was not disclosed under the exchange's publication rule/threshold.
- `no_trading`: date is valid but the requested instrument did not trade / was not listed where this can be distinguished reliably.
- `source_failure`: network, WAF, malformed provider payload, unexpected page format or business error. This must raise/classify a `FinancialDataError` rather than masquerading as a valid empty result.

The parser must not infer `not_published_by_rule` from an arbitrary HTTP 404/empty body. It needs positive provider context or a verified list/table that shows the scope is absent.

## Derived aggregation layer

Add a separate helper module/function, conceptually:

```python
aggregate_position_rankings(
    rows,
    top_n=(5, 10, 20),
    market_totals=None,
)
```

For each `trade_date + exchange + scope_id`, derive:

- `volume_top5/10/20` and changes;
- `long_top5/10/20` and changes;
- `short_top5/10/20` and changes;
- `long_minus_short_top5/10/20`.

### Concentration rule

Concentration is calculated only when a valid denominator is supplied explicitly:

- volume concentration denominator: total contract/product trading volume with matching scope/date/unit;
- long/short concentration denominator: total open interest with matching scope/date/unit.

Never divide top-N member sums by an unrelated dominant-contract or product-wide denominator.

### Net-position warning

`long_topN - short_topN` is a **derived ranking indicator**, not the full market net position and not a member-level net position. Long and short top-N lists can contain different members. Output metadata must label the formula and limitation.

## Exchange-specific source design

Each exchange keeps its own transport/parser. Shared code is limited to canonical-row construction, member-name normalization, publication envelope validation and derived aggregation.

### SHFE

Official current source family:

- public report page: `https://www.shfe.com.cn/reports/tradedata/dailyandweeklydata/?query_params=pm`
- current machine-data family discovered/used by current open-source integrations: `https://www.shfe.com.cn/data/tradedata/future/dailydata/pmYYYYMMDD.dat`
- structured rows use the `o_cursor` family with fields corresponding to volume, buy OI, sell OI, changes and participant abbreviations.

SHFE officially states that ranking publication depends on contract open-interest thresholds. The fetcher must therefore support `not_published_by_rule`.

### INE

Official current report page:

- `https://www.ine.cn/reports/tradedata/dailyandweeklydata/?query_params=pm`

The UI/report semantics mirror the SHFE-style daily ranking table, including member/overseas special participant rankings. INE remains a separate source ID and fetcher. Its exact machine path must be verified before the exchange capability is marked READY; schema similarity alone is not sufficient.

### DCE

Current official-source integration family uses DCE member-deal-position query/export endpoints under `memberDealPosiQuotes`, including contract-specific ranking requests. The implementation should separate:

1. contract/product discovery;
2. ranking data fetch;
3. parser.

Do not assume DCE scope semantics equal SHFE scope semantics. Preserve `scope_type` based on what the source actually publishes.

### CZCE

Modern official history uses the `FutureDataHolding` family, including paths such as:

`.../DFSStaticFiles/Future/YYYY/YYYYMMDD/FutureDataHolding.htm`

CZCE has multiple historical layout regimes. v0.2.3 should expose the modern verified regime first; unsupported older layouts must fail explicitly or remain RECIPE rather than being guessed.

### CFFEX

Official page:

- `https://www.cffex.com.cn/ccpm/`

Current historical CSV family used by integrations:

- `.../sj/ccpm/YYYYMM/DD/YYYYMMDD_1.csv`

CFFEX explicitly describes volume and positions in contracts/lots and applies publication rules/thresholds. The generic parser should preserve both futures and options if present; a futures-only convenience filter must be explicit.

### GFEX

Official product pages expose `日成交持仓排名` as a first-class statistical dataset. Current integration request family uses:

- `/u/interfacesWebTiMemberDealPosiQuotes/loadListContract_id`
- `/u/interfacesWebTiMemberDealPosiQuotes/loadList`

The fetcher should discover available contracts for date/product first, then request contract ranking data. Preserve exact source product/contract aliases in `raw`.

## Proposed public API

New module:

`financial_data.cn_futures_positioning`

Pure parsers / helpers:

- `normalize_member_name(name)`
- `validate_position_rank_row(row)`
- `aggregate_position_rankings(rows, top_n=(5, 10, 20), market_totals=None)`

Exchange fetchers:

- `fetch_shfe_position_rankings(...)`
- `fetch_ine_position_rankings(...)`
- `fetch_dce_position_rankings(...)`
- `fetch_czce_position_rankings(...)`
- `fetch_cffex_position_rankings(...)`
- `fetch_gfex_position_rankings(...)`
- `fetch_cn_futures_position_rankings(exchange, ...)`

The umbrella dispatcher is thin and never hides exchange-specific publication metadata.

## Capability model

Add exchange-level capabilities:

- `cn_futures_positions_shfe`
- `cn_futures_positions_ine`
- `cn_futures_positions_dce`
- `cn_futures_positions_czce`
- `cn_futures_positions_cffex`
- `cn_futures_positions_gfex`

Umbrella capability:

- `cn_futures_member_positions`

READY promotion rule per exchange:

1. real fetch/parser function exists;
2. deterministic fixture tests cover valid rows and malformed/provider failure;
3. publication/no-publication semantics are explicit;
4. rank/member/value/change fields are validated;
5. source URL and scope semantics are documented;
6. machine path/request shape is verified for the supported regime.

The umbrella capability becomes READY only when all six exchange capabilities meet the rule. Partial exchange coverage must not be hidden behind an umbrella READY label.

Capability Index increments from v5 to v6 only when the catalog changes are committed.

## Validation

A canonical ranking row is invalid if:

- `trade_date`, `exchange`, `scope_type`, `scope_id`, `ranking_type`, `rank`, `member_name`, `value`, `source_id` or `source_url` is missing;
- `scope_type` is not `contract` or `product`;
- `ranking_type` is not `volume`, `long` or `short`;
- `rank <= 0`;
- `value < 0`;
- `change` is non-numeric when present;
- contract scope lacks `contract_id`;
- a source-error page is parsed as ranking facts.

Duplicate rows with the same `(trade_date, exchange, scope_id, ranking_type, rank)` are rejected unless provider metadata explicitly distinguishes categories.

## Testing strategy

Use TDD with deterministic provider fixtures or minimal representative payloads.

Required tests:

1. long-form fact construction/validation;
2. independent volume/long/short ranking lists do not get falsely joined;
3. member-name preservation/normalization;
4. top5/top10/top20 sums and changes;
5. concentration requires a matching explicit denominator;
6. `long_topN - short_topN` is marked derived;
7. published vs not-published vs source-failure status;
8. SHFE structured ranking payload;
9. INE supported current payload/path once verified;
10. DCE contract/product discovery + ranking response;
11. CZCE modern holding layout;
12. CFFEX ranking CSV/table and optional futures-only filter;
13. GFEX contract discovery + ranking response;
14. dispatcher routes all supported exchanges;
15. Python 3.9 syntax/compile compatibility.

Live endpoint smoke checks, if performed, are timestamped `last_verified` evidence and never replace deterministic parser tests.

## Provenance and interpretation rules

- Official exchange data is the source of record.
- Open-source wrappers may be used to discover request shapes and historical pitfalls, but wrapper names are not the final `source_id`.
- Exchange member rankings are disclosed member-level statistics, not account-level or beneficial-owner positions.
- Futures-company rankings generally reflect the exchange's disclosed member/participant category and must not be described as the firm's own directional book unless the exchange explicitly says so.
- Top-N lists are truncated disclosure views; do not call them full-market positioning.

## Documentation

Create/update:

- `references/futures-positioning-ready-core.md`
- `references/futures-positioning-warehouse.md`
- `references/capability-index.yaml`
- `README.md`
- Draft PR #1 body

The new READY page should include copy-ready examples for raw rankings, top-N summaries and combining positioning with v0.2.2 daily market rows.

## Branch safety

All work remains on `feat/financial-data-skill` and Draft PR #1. Do not merge, force-rewrite or intentionally modify `main`.

## Source verification snapshot

Checked 2026-08-16:

- SHFE official site exposes `日交易排名`; SHFE publication rules state that ranking disclosure depends on contract open-interest thresholds.
- INE official site exposes `日交易排名` and the same class of member/overseas special participant ranking report.
- CFFEX official site exposes `成交持仓排名` and documents publication thresholds plus volume/OI units.
- GFEX official product pages expose `日成交持仓排名`.
- Current open-source integrations document modern SHFE `pmYYYYMMDD.dat`, DCE `memberDealPosiQuotes`, CZCE `FutureDataHolding`, CFFEX `sj/ccpm` CSV and GFEX `interfacesWebTiMemberDealPosiQuotes` request families. Each path must still pass the READY verification rule above before catalog promotion.
