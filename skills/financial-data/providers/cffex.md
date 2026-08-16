# Provider: CFFEX / 中国金融期货交易所

last_verified: 2026-08-16

## Identity
Official source of record for CFFEX daily statistics,成交持仓排名、交易/结算参数 and delivery data. Current public daily statistics state volume/OI are in contracts (single-sided) and turnover is in 万元.

## Access and authentication
Public daily statistics and ranking pages are viewable without account. Separate Level-1/Level-2/minute historical data products have application/purchase processes and are not equivalent to the free daily pages.

## Technical request limits
Official published QPS/RPM/concurrency limit for public daily/ranking downloads: **unknown**. Use daily cached requests and avoid crawling. Licensed historical products follow their application/data agreement rather than this public-web guidance.

## Data-range limits
Public daily/ranking CSV/file history has report-specific coverage. Higher-frequency historical Level-1/Level-2/1m/5m products are separate licensed products.

## Freshness and publication timing
Daily statistics and rankings are post-close. Ranking disclosure rules depend on product/open-interest thresholds; no row can be a valid non-publication state.

## Licensing and redistribution
Public daily facts are official; higher-frequency historical products and行情授权 have explicit authorization channels. Verify CFFEX information-management/market-data terms before redistribution.

## Data-quality limitations
Public daily turnover unit is `万元`; keep settlement vs close separate. Position rankings disclose top members under stated thresholds and are not full-account look-through data.

## Copy guidance
See `../references/futures-ready-core.md`, `../references/futures-positioning-ready-core.md`; runtimes `../scripts/financial_data/cn_futures_official.py`, `../scripts/financial_data/futures_positioning.py`. Freeze product code, date URL family, CSV encoding, disclosure scope and unit map.