# financial-data Futures READY Core Design

## Context

`financial-data` is handbook-first: downstream projects discover a capability here, copy the relevant source/normalization logic, and then own their recurring data workflow. The current futures layer already has deterministic local analytics (`select_dominant_contract`, `term_structure`, `calendar_spread`, `basis`, `roll_adjustment`) but the China futures source layer is still mostly RECIPE-level.

The user approved the next optimization round as **v0.2.2 Futures READY Core**: promote stable, high-value official China futures data paths into reusable helpers without turning all exchange websites into one fragile mega-adapter.

## Goal

Provide reusable official-source helpers for China futures daily market/settlement data, with exchange-specific parsers feeding one canonical futures row contract, then connect those rows to the existing dominant/curve/basis utilities.

## Options considered

### Option A — One universal exchange adapter

Expose one parser/fetcher with many exchange branches.

Pros: smallest public API.  
Cons: exchange formats, request methods, encodings and historical regimes are materially different; one provider change can destabilize unrelated exchanges.

### Option B — Exchange-specific fetch/parser + canonical row **(selected)**

Keep SHFE, INE, DCE, CZCE, CFFEX and GFEX transport/parsing isolated. Normalize only after provider parsing.

Pros: failures are isolated, fixtures are understandable, exchange migrations are local, provenance stays exact.  
Cons: more files/functions, but this is appropriate for a handbook/reusable-source library.

### Option C — Depend directly on AkShare/Tushare wrappers

Pros: quickest coverage.  
Cons: hides upstream endpoint/field changes and error semantics, adds a heavy dependency, weakens provenance, and does not fit the Skill's project-extraction purpose.

## Architecture

Create `financial_data/cn_futures_official.py` as the shared namespace. Provider-specific functions remain explicit:

- `fetch_shfe_daily(trade_date, ...)`
- `fetch_ine_daily(trade_date, ...)`
- `fetch_dce_daily(trade_date, ...)`
- `fetch_czce_daily(trade_date, ...)`
- `fetch_cffex_daily(trade_date, ...)`
- `fetch_gfex_daily(trade_date, ...)`
- `fetch_cn_futures_daily(exchange, trade_date, ...)` as a thin dispatcher only

Each transport has a paired pure parser so fixtures can be tested without network:

- JSON parsers for SHFE/INE and JSON POST-style DCE/GFEX responses
- CSV/ZIP parser for CFFEX historical daily files
- text/download parser for CZCE, preserving historical encoding/layout differences

Do **not** make these six parsers share provider-specific field lookup code merely to reduce lines; the normalization boundary is the shared layer.

## Canonical futures daily row

Every contract row normalizes to the same required keys:

```python
{
    "contract_id": "CU2609",
    "variety": "CU",
    "exchange": "SHFE",
    "trade_date": "2026-08-14",
    "open": 0.0,
    "high": 0.0,
    "low": 0.0,
    "close": 0.0,
    "settlement": 0.0,
    "pre_settlement": 0.0,
    "volume": 0,
    "turnover": 0.0,
    "open_interest": 0,
    "currency": "CNY",
    "volume_unit": "contracts",
    "turnover_unit": "provider_declared",
    "source_id": "shfe",
    "source_url": "...",
}
```

Optional keys may include `open_interest_change`, `delivery_month`, `product_name`, `raw`, and provider-specific metadata.

### Unit rule

Do not globally assume turnover units are identical across exchanges. For example, CFFEX's public daily statistics describe turnover in ten-thousand yuan and volume/open interest in contracts/lots. Each exchange parser records its declared source unit and only converts to CNY when the source definition is explicit and tested.

### Settlement rule

`close`, `settlement`, and `pre_settlement` are separate fields. No fallback substitution is allowed between them.

## Official-source families

The implementation will preserve the source page and actual machine path separately.

### SHFE

Official statistics expose daily trading, ranking, settlement parameters, warehouse receipts and inventory reports. Daily contract data currently uses the SHFE official data family with `o_curinstrument`-style structured rows. SHFE and INE parsing can share canonical normalization helpers but not source IDs or URL assumptions.

### INE

Official daily/weekly statistics expose daily trading, rankings, settlement parameters, warehouse receipts and inventory reports. Treat INE as a separate exchange/source even where the schema resembles SHFE.

### DCE

Use the official DCE daily statistics request family. The current implementation-discovery path shows JSON contract rows with explicit open/high/low/close, last settlement, settlement, volume, open interest and turnover fields. Keep DCE variety-name→code mapping explicit and test it.

### CZCE

CZCE has meaningful historical format/encoding changes. The fetch layer may choose a date-dependent official download path; parser fixtures must cover the current text layout and at least one historical layout if historical support is exposed. Do not silently return an empty list when the provider serves an error page.

### CFFEX

Use official daily/historical data. Preserve contract rows and exclude summary rows; do not automatically drop options in the generic parser. If a futures-only convenience function is provided, filtering must be explicit.

### GFEX

Use the official daily quote data family. Preserve exchange-provided `clearPrice`, `lastClear`, `openInterest`, volume and turnover semantics. Product codes such as `SI`, `LC`, `PS`, `PT`, `PD` are normalized without changing case-sensitive source aliases stored in `raw`.

## Capability model

Split the existing broad capability into exchange-level capabilities:

- `cn_futures_daily_shfe`
- `cn_futures_daily_ine`
- `cn_futures_daily_dce`
- `cn_futures_daily_czce`
- `cn_futures_daily_cffex`
- `cn_futures_daily_gfex`

Only mark an exchange capability `READY` when:

1. its fetch/parser function exists;
2. deterministic parser tests exist;
3. provider business/error pages are not represented as successful empty data;
4. units and settlement semantics are documented;
5. the capability index points to the real runtime function.

The umbrella `cn_futures_daily_settlement` becomes READY only when all six exchange capabilities satisfy these rules.

## Data flow

```text
Official exchange endpoint/download
        ↓
exchange-specific transport
        ↓
exchange-specific pure parser
        ↓
canonical futures daily rows
        ↓
validation
        ↓
existing futures analytics
  ├─ select_dominant_contract
  ├─ term_structure
  ├─ calendar_spread
  ├─ basis
  └─ roll_adjustment
        ↓
project export / TradingView / research workflows
```

## Validation

Add reusable futures-row validation:

- `high >= max(open, low, close)` when all four are present;
- `low <= min(open, high, close)`;
- volume/open interest/turnover are non-negative when present;
- contract ID and trade date are required;
- settlement/pre-settlement remain independent fields;
- summary rows such as `小计`/`总计` are excluded at provider parsing;
- invalid provider payload/error HTML raises `FinancialDataError` rather than returning an empty success.

## Scope of v0.2.2

### In scope

1. Official daily contract market/settlement data for the six China futures exchanges.
2. Canonical row contract and validation.
3. Dispatcher by exchange.
4. Direct compatibility with existing dominant/term-structure helpers.
5. Capability Index / recipe / README updates.
6. Deterministic fixtures and tests.

### Deferred to subsequent sub-phases

The following remain separate because their schemas and business semantics differ from daily contract quotes:

- member position rankings;
- warehouse receipts / inventory;
- daily margin/limit/fee parameter snapshots;
- delivery statistics;
- intraday/CTP market data.

They remain documented in the handbook and will be promoted in follow-on READY batches, preferably in that order: **member positioning → warehouse/inventory → trading parameters → intraday CTP**.

## Testing strategy

TDD per exchange parser. Tests use saved representative provider payloads/text/CSV rather than live requests. Required behaviors:

- valid contract rows normalize correctly;
- summary rows are removed;
- empty but valid trading-day response is distinguishable from provider failure;
- malformed/provider-error payload raises an explicit error;
- turnover units are preserved/converted according to exchange-specific rules;
- dominant selection and term structure accept normalized rows without exchange-specific glue.

Live endpoint smoke checks are a separate verification layer and are not required to claim parser correctness. Any live check must be timestamped and recorded as `last_verified`, not silently converted into a permanent guarantee.

## Source/provenance policy

Official exchange URLs remain the source of record. AkShare or other open-source wrappers may be used only to discover current request shapes/field names and must not become the declared data source. If substantive implementation code is copied, preserve its license/attribution; otherwise independently implement the small transport/parser from the documented provider schema.

## Branch safety

All changes stay on `feat/financial-data-skill` / Draft PR #1. No merge or force rewrite of `main`.
