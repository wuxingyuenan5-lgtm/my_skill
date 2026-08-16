# Futures Positioning READY Core

## What this layer is

`financial_data.futures_positioning` normalizes exchange-published member trading/position rankings into a long-form fact table and provides provider-agnostic Top-N analytics.

It is **not** a full-market positioning feed and it is **not** a member proprietary-account signal. Exchange rankings are disclosure subsets and may be subject to publication thresholds.

## Canonical fact

One row is one ranking observation:

```python
{
    "trade_date": "2026-08-14",
    "exchange": "SHFE",
    "scope_type": "contract",
    "scope_id": "CU2609",
    "variety": "CU",
    "contract_id": "CU2609",
    "ranking_type": "long",   # volume | long | short
    "rank": 1,
    "member": "某期货",
    "value": 12345,
    "change": -321,
    "source_id": "shfe",
    "source_url": "...",
    "raw": {...},
}
```

### Why long-form

The exchange's volume rank #1, long rank #1 and short rank #1 may be three different members. Do not merge those three rows into a fake single-member record merely because their rank number is the same.

Wide tables remain useful for display/export only; the internal fact model stays long-form.

## Publication status

A fetch result contains:

```text
published
not_published_by_rule
no_trading
source_failure
```

A valid empty ranking payload is not automatically a source outage. Several exchanges publish rankings only when disclosure conditions are met.

Where a parser cannot distinguish threshold non-publication from another valid empty case, the result carries `details.empty_payload_status_inferred=true`.

Malformed payloads, WAF pages, invalid ZIP/XLSX/CSV and HTTP failures raise `FinancialDataError`; they do not return a successful empty result.

## READY matrix in v0.2.3

| Exchange | Status | Runtime | Boundary |
|---|---|---|---|
| SHFE | READY | `fetch_shfe_positions` | current official `pmYYYYMMDD.dat` family |
| INE | RECIPE/parser-ready | `parse_ine_position_payload` | official Daily Ranking page confirmed; machine fetch path not frozen because current site access can trigger WAF |
| DCE | READY | `fetch_dce_positions` | official batch member-position ZIP family |
| CZCE | READY | `fetch_czce_positions` | current XLSX regime from `2025-11-02`; older XLS/XLS-text regimes remain recipe/history |
| CFFEX | READY | `fetch_cffex_positions` | current product CSV family under `/sj/ccpm/`; caller supplies product code such as `IF` |
| GFEX | READY | `fetch_gfex_positions` | current variety/contract discovery + three `data_type` ranking pages; caller supplies variety |

The umbrella `cn_futures_member_positions` remains **RECIPE** until INE transport is frozen as READY. This is intentional partial readiness, not a failure of the other five exchange helpers.

## Public API

```python
from financial_data import fetch_cn_futures_positions

shfe = fetch_cn_futures_positions("SHFE", "2026-08-14")

dce = fetch_cn_futures_positions("DCE", "2026-08-14")

cffex = fetch_cn_futures_positions(
    "CFFEX",
    "2026-08-14",
    product="IF",
)

gfex = fetch_cn_futures_positions(
    "GFEX",
    "2026-08-14",
    variety="lc",
)
```

INE currently fails explicitly through the dispatcher rather than guessing a machine path:

```python
fetch_cn_futures_positions("INE", "2026-08-14")
# FinancialDataError(FIELD_NOT_SUPPORTED, ... parser exists but transport is not frozen as READY)
```

## Top-N analytics

```python
from financial_data import (
    aggregate_standard_windows,
    aggregate_top_n,
    position_denominators_from_daily,
)

facts = shfe["rows"]
metrics = aggregate_top_n(facts, 20)
```

Output includes:

```text
volume
volume_change
long
long_change
short
short_change
long_minus_short
concentration.volume
concentration.long
concentration.short
```

`long_minus_short` means:

```text
sum(disclosed top-N long ranking values)
-
sum(disclosed top-N short ranking values)
```

It is a **derived disclosed-subset imbalance**, not the exchange's full-market net position.

## Concentration denominator rule

Ranking rows alone do not contain a valid concentration denominator.

Use the v0.2.2 exact-contract daily row:

```python
den = position_denominators_from_daily(daily_rows, "CU2609")
metrics = aggregate_top_n(facts, 20, den)
```

Rules:

- volume concentration denominator = same contract/day total `volume`;
- long concentration denominator = same contract/day total `open_interest`;
- short concentration denominator = same contract/day total `open_interest`;
- missing or non-positive denominator => concentration is `None`, never guessed.

## Exchange notes

### SHFE

The official site exposes Daily Ranking and the current structured data family uses fields such as:

```text
RANK
INSTRUMENTID
PARTICIPANTABBR1 / CJ1 / CJ1_CHG
PARTICIPANTABBR2 / CJ2 / CJ2_CHG
PARTICIPANTABBR3 / CJ3 / CJ3_CHG
```

The three participant columns correspond to volume, long OI and short OI ranking lists.

### INE

The official site currently exposes Daily Ranking and its information rules explicitly include member trading-volume and open-interest rankings. However automated access to the current Daily Ranking page may trigger WAF/human verification. The shared parser supports SHFE-style `o_cursor` facts, but the common fetch dispatcher does not declare INE READY until the machine path is independently frozen.

### DCE

The current discovery route uses the official batch endpoint:

```text
/dcereport/publicweb/dailystat/memberDealPosi/batchDownload
```

The returned ZIP contains per-contract text files with three independent sections: volume ranking, long-position ranking and short-position ranking.

### CZCE

Current 2026 positioning downloads use:

```text
/cn/DFSStaticFiles/Future/YYYY/YYYYMMDD/FutureDataHolding.xlsx
```

The READY fetcher is deliberately bounded to the current XLSX regime (`2025-11-02+`). Historical XLS/HTML/text layouts remain separate recipes rather than being silently guessed.

### CFFEX

The official website exposes `成交持仓排名`. The current product CSV family is:

```text
/sj/ccpm/YYYYMM/DD/PRODUCT_1.csv
```

Examples: `IF`, `IC`, `IM`, `IH`, `T`, `TF`, `TS`, `TL`.

CFFEX publishes ranking data subject to disclosure rules/thresholds. A missing ranking is not automatically a network failure.

### GFEX

The official product pages expose `日成交持仓排名`. Current request discovery uses:

```text
/u/interfacesWebTiMemberDealPosiQuotes/loadListContract_id
/u/interfacesWebTiMemberDealPosiQuotes/loadList
```

`data_type=1/2/3` corresponds to the three independent ranking lists consumed by the canonical layer.

## Operational guidance

- Prefer collection after the exchange's daily publication window; do not assume ranks are final immediately at market close.
- Save `source_url`, retrieval timestamp in the downstream project, parser version and raw payload/file hash.
- Treat WAF/403/429 as source-health events and route to licensed fallbacks when production continuity matters.
- Do not redistribute exchange data commercially merely because the helper can retrieve it; verify the relevant exchange information-use terms.

## Next batch

After positioning, the recommended READY sequence remains:

1. warehouse receipts / inventory;
2. trading parameters (margin, price limits, fees, delivery/session parameters);
3. CTP / licensed intraday data.
