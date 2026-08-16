# financial-data

Version: **0.2.3 handbook-first**

A cross-asset **financial-data engineering handbook + source recipe library + reusable utility kit** for Agents. The primary use case is project initialization: discover a dataset once, select source/fallback/field semantics, export the required recipe/module into the downstream project, and let that project own its recurring workflow.

## Start here

1. Search `references/capability-index.yaml` by asset class / market / dataset.
2. Read the referenced handbook page.
3. Check capability state: `READY`, `RECIPE`, `RESTRICTED`, `DEGRADED`, `DEPRECATED`.
4. Freeze only the selected recipe/module into the target project using `references/project-export.md`.

The handbook is intentionally broad. Size is not a design constraint; navigability and engineering completeness are.

## Coverage

### A-shares

Quotes, K-lines, order book/ticks, index/ETF, market-wide cross-sections, statements/F10/filings, research/consensus, fund flow, margin, dragon-tiger, block trades, holders, lockups, dividends, sector flow, limit-up/break/down pools, previous-limit performance, watch/anomaly pools, IRM, hot/popularity lists and news/flash recipes.

### US/HK/global equities

Quotes/K-lines, market lists/search/news, SEC filings/XBRL, SEC Frames/daily filing stream/full-text, vendor valuation/consensus/holdings, CFTC positioning, FINRA daily short volume, earnings calendars and options recipes.

### Futures/commodities

SHFE/INE/DCE/CZCE/CFFEX/GFEX plus global source families; exact-contract master, official China daily OHLC/settlement READY core, dominant selection, continuous-roll methodology, night-session trading date, settlement vs close, term structure, calendar spreads, basis, member rankings/Top-N positioning, warehouse/inventory, margin/limits/fees and delivery metadata.

Daily exact-contract market/settlement data is READY for all six domestic exchanges. Member positioning is currently READY for **SHFE / DCE / CZCE / CFFEX / GFEX**; INE has a parser and official-page recipe but its current machine transport is deliberately not marked READY until the WAF/machine-download path is frozen independently.

### Options

US CBOE/Yahoo and China ETF option chains/T-quotes/Greeks/IV with explicit licensing/model semantics.

### Visualization

TradingView Widgets, Advanced Charts/Datafeed/UDF, Lightweight Charts, custom data conversion, futures sessions/symbol mapping and reusable frontend/backend templates.

### Professional sources

Wind, Choice, Bloomberg, LSEG/Refinitiv, Tushare Pro, CTP/broker/exchange L1/L2 and crypto exchange APIs are recorded as licensed/restricted source families where applicable.

## Capability states

- **READY**: a reusable shared runtime helper/adapter/template exists in this repo.
- **RECIPE**: complete project-copy guidance exists but common facade integration is intentionally optional.
- **RESTRICTED**: source/library requires key, entitlement, paid license or permission.
- **DEGRADED**: known upstream issue; use fallback.
- **DEPRECATED**: migration/history only.

## Shared runtime

Core Python remains lightweight (`requests` + stdlib).

Current reusable data adapters/helpers include:

- **Tencent** — CN quote/price/turnover/valuation plus A-share K-lines (`1m`→monthly; daily/weekly/monthly support qfq/hfq/none).
- **Sina** — independent CN quote/price fallback.
- **Yahoo v8 Chart** — US/HK K-lines with timezone/null/error/adjclose handling.
- **EastmoneyClient** — throttled datacenter queries, Push2 market lists and US/HK security discovery; specialized Eastmoney datasets remain recipe-level.
- **China futures official daily** — SHFE/INE/DCE/CZCE/CFFEX/GFEX daily exact-contract OHLC, close/settlement/pre-settlement, volume, turnover and open interest normalized into one canonical row. See `references/futures-ready-core.md`.
- **China futures positioning** — long-form volume/long/short member-ranking facts plus Top5/10/20 sums, disclosed-subset long-minus-short and denominator-safe concentration. Five exchanges have READY fetchers; INE remains parser/recipe until transport is frozen. See `references/futures-positioning-ready-core.md`.
- **SEC EDGAR** — filings/companyfacts standard metrics.
- **SEC official helpers** — Frames and Daily Master Index.
- **US Treasury** — yield curve / 2Y / 10Y / 10Y-2Y.
- **CFTC** — COT query/parser helper.

Local analytics provide MA/EMA/RSI/MACD/KDJ/Bollinger/volatility/drawdown/breadth/concentration.

Examples:

```python
from financial_data import (
    DataRequest,
    EastmoneyClient,
    aggregate_standard_windows,
    fetch_cn_futures_daily,
    fetch_cn_futures_positions,
    get_data,
    position_denominators_from_daily,
)

cn_bars = get_data(DataRequest(
    "600519.SH", "kline",
    params={"resolution": "1d", "adjustment": "qfq", "count": 250},
))

us_bars = get_data(DataRequest(
    "AAPL.US", "kline",
    params={"interval": "1d", "range": "1y"},
))

em = EastmoneyClient(min_interval=1.0)
market = em.market_stock_list("us_nasdaq", sort_field="f3", page_size=50)
hits = em.search_securities("Tencent")

lc_rows = fetch_cn_futures_daily("GFEX", "2026-08-14")
lc_rows = [row for row in lc_rows if row["variety"] == "LC"]

shfe_positions = fetch_cn_futures_positions("SHFE", "2026-08-14")
cu_daily = fetch_cn_futures_daily("SHFE", "2026-08-14")
cu_denominators = position_denominators_from_daily(cu_daily, "CU2609")
cu_facts = [row for row in shfe_positions["rows"] if row["scope_id"] == "CU2609"]
cu_positioning = aggregate_standard_windows(cu_facts, cu_denominators)
```

Reusable engineering utilities:

```python
from financial_data.charting import to_tradingview_bar, to_udf_history, to_lightweight_bar
from financial_data.futures import select_dominant_contract, term_structure, calendar_spread, basis, roll_adjustment
from financial_data.project_export import build_project_manifest

# Exact-contract rows from the official futures READY core can feed these directly.
dominant_lc = select_dominant_contract(lc_rows, metric="open_interest")
lc_curve = term_structure(lc_rows, price_field="settlement")
```

Structured `bar` DataPoints and canonical futures rows are validated before delivery; provider/network failures are never represented as successful empty data.

## Futures positioning rule

Member rankings are **disclosure subsets**, not full-market positions. The volume ranking, long-OI ranking and short-OI ranking are independent lists; identical rank numbers do not imply the same member.

`aggregate_standard_windows()` derives Top5/10/20 sums and `long_minus_short`. That derived imbalance is not a full-market net position. Concentration is calculated only when a same-contract, same-trading-day denominator is explicitly supplied:

- volume ranking / total contract volume;
- long ranking / contract open interest;
- short ranking / contract open interest.

If the denominator is missing or non-positive, concentration stays `None` rather than being estimated.

The umbrella `cn_futures_member_positions` capability remains RECIPE while INE transport is not frozen; exchange-specific READY entries exist for SHFE/DCE/CZCE/CFFEX/GFEX.

## TradingView project templates

`assets/tradingview/` contains:

- `widget.html` — TradingView-supplied public-symbol embed pattern.
- `lightweight-chart.html` — own-data Lightweight Charts example.
- `datafeed-template.js` — Advanced Charts custom Datafeed bridge, without proprietary library files.
- `udf-fastapi-example.py` — minimal `/config` `/search` `/symbols` `/history` `/time` backend.

Advanced Charts library files are not redistributed in this public repository.

## Futures utility rule

`fetch_cn_futures_daily()` returns real exchange contract rows; it does not manufacture a “main” or continuous contract. `select_dominant_contract()` only selects from supplied exact contracts according to an explicit metric. `term_structure`, `basis`, `calendar_spread` and `roll_adjustment` are local methodology helpers and require consistent units/times.

For cross-exchange turnover comparisons, check `turnover_unit` first. CFFEX and CZCE rows with an explicit 万元 source field use `CNY_10K`; other exchange daily parsers currently preserve `provider_declared` until their conversion methodology is frozen independently.

## Project extraction

Use `build_project_manifest()` or `references/project-export.md` to create a project-local source pack. Keep canonical fields, fallbacks, credentials, parser fixtures, health checks and `last_verified` in the downstream project after extraction.

## Compliance

Tencent, Yahoo and Eastmoney shared helpers are **research integration conveniences**, not evidence of commercial redistribution rights. Yahoo v8 Chart itself does not require cookie/crumb in this implementation, while other Yahoo endpoint families may. Eastmoney defaults to conservative serial throttling; do not disable it for full-market concurrency without understanding provider risk controls.

Official exchange public data helpers likewise do not replace a project-specific review of current website/API terms, redistribution rights or commercial market-data licensing obligations.

## Attribution

Source discovery and many provider pitfalls were informed by Apache-2.0 `simonlin1212/a-stock-data` and `simonlin1212/global-stock-data`. Current futures endpoint/request-shape discovery was cross-checked against Apache-2.0 AkShare source, while the declared source of record remains the underlying exchange. Preserve upstream notices if substantive upstream implementation code is later copied.

## Common runtime quick start

```bash
pip install requests pytest
export PYTHONPATH="$PWD/skills/financial-data/scripts:$PYTHONPATH"
python -m pytest skills/financial-data/tests -q
python3 scripts/validate_skills.py
```
