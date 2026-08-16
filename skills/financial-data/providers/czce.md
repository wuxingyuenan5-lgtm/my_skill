# Provider: CZCE / 郑州商品交易所

last_verified: 2026-08-16

## Identity
Official source of record for CZCE futures/options statistics, member rankings, warehouse/delivery and trading-rule data.

## Access and authentication
Public static report files/pages are generally research-accessible without API key, but no stable public API SLA is assumed. Access controls and path conventions can change.

## Technical request limits
Official published QPS/RPM/concurrency limit: **unknown**. Use one/few cached report downloads per trading day, avoid aggressive historical crawling, and back off on errors.

## Data-range limits
CZCE has multiple historical file formats/path regimes. The current shared daily READY path is explicitly scoped to the modern regime; the current positioning reference fetch is scoped to the XLSX holding-report regime from 2025-11-02 onward. Older history remains a separate recipe problem.

## Freshness and publication timing
Post-close daily data; exact publication timestamp is report-dependent and not represented as a guaranteed SLA.

## Licensing and redistribution
Official public source for research; commercial redistribution/licensing must be checked against current CZCE information/data terms.

## Data-quality limitations
Contract codes and historical year/month encoding require care. Preserve raw header units, especially turnover; do not silently coerce error pages into empty successful data.

## Copy guidance
See `../references/futures-ready-core.md`, `../references/futures-positioning-ready-core.md`; reference runtimes `../scripts/financial_data/cn_futures_official.py`, `../scripts/financial_data/futures_positioning.py`. Freeze date regime, file format, encoding/unit rules and sample fixture.