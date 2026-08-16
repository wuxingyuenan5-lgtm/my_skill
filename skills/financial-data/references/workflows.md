# Reusable Financial-Data Workflows

These workflows describe how to assemble datasets. Investment interpretation belongs to the calling research/strategy layer.

## 1. Project data-module initialization

1. Translate requirements into capability IDs via `capability-index.yaml`.
2. Select primary/fallback sources and status (`READY/RECIPE/RESTRICTED`).
3. Freeze canonical instruments, fields, unit/time/PIT semantics and validation tolerances.
4. Use `project-export.md` / `financial_data.project_export` to prepare a project manifest.
5. Copy only required recipes/modules/assets into the downstream project.
6. Add parser fixtures/source-health checks and let the project own recurring refreshes.

## 2. Single-stock research dataset

Quote/market cap/valuation → latest filing + financial facts → consensus/research metadata → formal industry + vendor concepts → flows/positioning/lockup/dragon-tiger → news/IRM. Preserve facts vs vendor estimates vs sentiment as separate layers.

## 3. Peer comparison

Resolve exact peer set and classification version → align report/forecast periods and currencies → collect valuation/financial/consensus metrics → flag missing/conflicting sources → deliver normalized table. Avoid comparing mixed TTM/FY1 values without labels.

## 4. A-share market/sector dashboard

Full-market quote/cross-section → index/style matrix → official industry membership → sector change/breadth/turnover share/fund flow → limit-up/break/down sentiment → optional margin/ETF/Connect data. Build one market-wide pull where possible rather than per-stock loops.

## 5. Futures monitor

Contract master → exact contract quotes/settlement/OI → dominant selection → term structure/calendar spreads → spot/basis → member positions/warehouse → margin/limit/fee changes → continuous series only after roll methodology is frozen.

## 6. SEC event/screener

Ticker↔CIK → submissions/company facts → daily filing stream/FTS for events → Frames for cross-sectional metrics → available_at rules for PIT use.

## 7. Options flow research

Exact option chain → expiry/0DTE filtering → bid/ask/volume/OI/IV/Greeks → local put-call/vol-OI/skew/delta-derived metrics. Treat derived flow signals as signals, not verified trader intent.

## 8. TradingView/custom visualization

Canonical bars/events → `charting.py` conversion → choose Widget vs Advanced Charts/Datafeed/UDF vs Lightweight Charts → generate symbol/session/resolution map from project instrument/calendar data → keep raw source adapters renderer-neutral.

## 9. Macro/PIT dataset

Official series + release calendar → store observation period, published/available time and vintage/revision → only then join to market data for historical analysis.
