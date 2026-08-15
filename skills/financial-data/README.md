# financial-data

Version: **0.1.0+ handbook expansion**

A reusable **financial-data engineering handbook + source library** for Agents. It is intended to be consulted when a project needs to discover, select, validate and permanently integrate financial data sources.

The target usage is often **one-time project extraction**: a project calls this Skill during setup, copies only the required data-source recipes/contracts/adapters into itself, and then owns its recurring data workflow independently.

## Architecture

```text
                    financial-data handbook
                 /          |            \
       source recipes   data contract   known issues
              ↓              ↓              ↓
Project requirement → source routing → canonical data
                                      ↓
                              validate / cache
                                      ↓
                         project-local data module
                                      ↓
             research / reports / TradingView / dashboards
```

The shared Python facade is a convenience layer. A capability can still be useful as a complete `RECIPE` even when it is not wired into the common runtime.

## Capability states

- `READY`: reusable shared adapter exists.
- `RECIPE`: complete copy-ready source recipe exists; shared runtime integration is optional.
- `RESTRICTED`: complete recipe but key/license/permission/paid access is required.
- `DEGRADED`: upstream issue exists; fallback required.
- `DEPRECATED`: migration/history reference only.

## Implemented common runtime in v0.1.0

- Unified `DataRequest` / `DataPoint` / `DataResult` contracts and explicit error codes.
- Instrument normalization for common A-share, HK, US equity/index and US Treasury aliases, including ambiguity guards.
- Source registry, source-health state, field-level routing, compliance filters and independent fallback ordering.
- Normalization/validation, cross-source tolerance checks, explicit `SOURCE_CONFLICT`, and compact/standard/full output profiles.
- Pure-Python returns, SMA/EMA, RSI, MACD, Bollinger, volatility, drawdown, percentile, turnover rate, turnover concentration, market breadth and KDJ.
- **Tencent**: CN quote/price/turnover/turnover rate/market cap/float market cap/PE/PB.
- **Sina**: independent CN quote/price fallback.
- **SEC EDGAR**: ticker→CIK, filing metadata, XBRL fundamentals including revenue, net income, operating cash flow, assets, liabilities and R&D expense.
- **US Treasury**: yield curve, 2Y, 10Y and derived 10Y–2Y spread.

The handbook is being expanded beyond the common runtime to preserve a much larger set of copy-ready market-data recipes.

## Futures is a first-class domain

See `references/futures-commodities.md`.

The futures handbook covers the engineering model for:

- SHFE / INE / DCE / CZCE / CFFEX / GFEX
- exact futures contracts
- dominant/main contracts
- continuous futures construction
- night-session `trade_date`
- close vs settlement
- open interest and member rankings
- warehouse receipts / inventory / delivery
- margin / limits / fees
- expiry and roll calendars
- term structure / calendar spreads
- basis and cross-market commodity normalization
- futures options
- global futures source families (CME/CBOT/NYMEX/COMEX, ICE, LME, Eurex, SGX, etc.)

A continuous futures series is always treated as a derived instrument with an explicit roll/adjustment methodology.

## TradingView integration

See:

- `references/chart-data-contract.md`
- `references/tradingview.md`

The Skill distinguishes four integration routes:

1. **TradingView Widgets** — embed TradingView-supplied market data for supported symbols.
2. **Advanced Charts / Charting Library** — full TradingView-style chart UI using the project's own Datafeed API or UDF backend.
3. **Lightweight Charts** — open-source TradingView chart components using project-supplied data directly.
4. **Trading Platform / Broker API** — broker/trading integration, separate from a data-only project.

The handbook includes:

- TradingView symbol aliases
- `LibrarySymbolInfo` mapping
- session/timezone/resolution mapping
- canonical OHLCV → Advanced Charts `Bar`
- UDF `/config`, `/search`, `/symbols`, `/history` structure
- real-time `subscribeBars` architecture
- futures-specific session/continuous-contract rules
- chart marks/events
- Advanced Charts custom-indicator vs Pine distinction
- Lightweight Charts own-data recipes
- generated project folder patterns

Do not use TradingView as an unofficial generic market-data scraping API. Raw market data should come from the appropriate source/exchange/vendor; TradingView is a visualization/integration layer unless a specific TradingView Widget explicitly provides the data.

## Project extraction

See `references/project-export.md`.

Example request:

> “Use financial-data to design a permanent data module for my A-share monitor: SW industry data + stock turnover + limit-up pool + TradingView charts.”

The Skill should produce only the needed pack, for example:

```text
data/
  sources.yaml
  contracts.yaml
  instruments.py
  industry.py
  market_data.py
  limit_pool.py
  validate.py
frontend/
  charts/
    data_adapter.js
    tradingview-or-lightweight.js
README.md
```

After extraction, the target project owns its adapters, credentials, cache, monitoring and parser fixtures.

## Install / use common runtime

Core runtime targets Python **3.9+** and requires `requests`.

```bash
pip install requests
export PYTHONPATH="$PWD/skills/financial-data/scripts:$PYTHONPATH"
```

```python
from financial_data import DataRequest, get_data, result_dict

r = get_data(DataRequest("600519", "quote", require_crosscheck=True))
print(result_dict(r, "compact"))
```

SEC automated access requires a truthful contact identity:

```bash
export SEC_CONTACT="Your Name your.email@example.com"
```

`SEC_CONTACT` is deliberately never hard-coded in the repository.

## Data guarantees

A standardized observation records its instrument, field/value/unit, relevant currency and dates, `source_id`, `as_of`, `retrieved_at`, status/quality flags, and optional provider/algorithm metadata. Percentages are stored as decimals. A source outage is never represented as an empty successful result.

For point-in-time research, publication/filing time is distinct from report period. For prices, adjustment convention must be explicit; for volume-like fields, distinguish shares/lots/contracts.

## Compliance

Source access and data rights are separate questions. The registry records commercial-use and redistribution posture, but classifications can change; re-check current source terms before commercial deployment. The Skill does not bypass CAPTCHA, access controls, robots restrictions, or explicit anti-scraping rules.

TradingView Advanced Charts/Trading Platform library files themselves are not to be copied into this public repository; downstream projects obtain access through TradingView's official process.

## Attribution

Architecture and source-discovery research were informed by the Apache-2.0 projects **`simonlin1212/a-stock-data`** and **`simonlin1212/global-stock-data`**. This repository uses a modular handbook/runtime approach rather than copying their large embedded `SKILL.md` code wholesale. If substantive upstream code is imported in a future version, retain the applicable Apache-2.0 notices and source attribution.

## Test common runtime

```bash
pip install pytest
python -m pytest skills/financial-data/tests -q
python3 scripts/validate_skills.py
```
