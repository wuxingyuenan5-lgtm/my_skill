# financial-data

Version: **0.2.0 handbook-first**

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

SHFE/INE/DCE/CZCE/CFFEX/GFEX plus global source families; exact-contract master, dominant selection, continuous-roll methodology, night-session trading date, settlement vs close, term structure, calendar spreads, basis, member positions, warehouse/inventory, margin/limits/fees and delivery metadata.

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

Core Python remains lightweight (`requests` + stdlib). Existing READY data adapters include Tencent CN quote, Sina quote fallback, SEC EDGAR filings/companyfacts and US Treasury. Local analytics provide MA/EMA/RSI/MACD/KDJ/Bollinger/volatility/drawdown/breadth/concentration.

New reusable engineering utilities:

```python
from financial_data.charting import to_tradingview_bar, to_udf_history, to_lightweight_bar
from financial_data.futures import select_dominant_contract, term_structure, calendar_spread, basis, roll_adjustment
from financial_data.project_export import build_project_manifest
```

## TradingView project templates

`assets/tradingview/` contains:

- `widget.html` — TradingView-supplied public-symbol embed pattern.
- `lightweight-chart.html` — own-data Lightweight Charts example.
- `datafeed-template.js` — Advanced Charts custom Datafeed bridge, without proprietary library files.
- `udf-fastapi-example.py` — minimal `/config` `/search` `/symbols` `/history` `/time` backend.

Advanced Charts library files are not redistributed in this public repository.

## Futures utility rule

`select_dominant_contract()` only selects from supplied exact contracts according to an explicit metric; it does not magically create a tradable “main contract.” `term_structure`, `basis`, `calendar_spread` and `roll_adjustment` are local methodology helpers and require upstream exact-contract/spot data with consistent units/times.

## Project extraction

Use `build_project_manifest()` or `references/project-export.md` to create a project-local source pack. Keep canonical fields, fallbacks, credentials, parser fixtures, health checks and `last_verified` in the downstream project after extraction.

## Attribution

Source discovery and many provider pitfalls were informed by Apache-2.0 `simonlin1212/a-stock-data` and `simonlin1212/global-stock-data`. This repo reorganizes them into a cross-asset handbook and new modular utilities rather than copying the giant embedded Skill files wholesale. Preserve upstream notices if substantive upstream implementation code is later copied.

## Common runtime quick start

```bash
pip install requests pytest
export PYTHONPATH="$PWD/skills/financial-data/scripts:$PYTHONPATH"
python -m pytest skills/financial-data/tests -q
python3 scripts/validate_skills.py
```
