# Provider: Eastmoney / 东方财富

last_verified: 2026-08-16

## Identity
Public financial-information vendor with Push2, datacenter and search endpoint families. Strong research source for A-share market cross-sections, lists and many vendor-derived datasets; not a formal exchange source of record.

## Access and authentication
Many currently used public-web endpoints work without API keys; some endpoint families may depend on cookies, referer or browser-like headers. Official automation contract: endpoint-dependent/unknown.

## Technical request limits
Official published global QPS/RPM limit: **unknown**. Repository default for the shared Eastmoney client is a conservative serial throttle (`min_interval=1.0s`), explicitly an **empirical safety setting, not an official limit**. Prefer batch/full-market endpoints over thousands of per-symbol calls; cache and back off on 403/429/temporary blocking.

## Data-range limits
Endpoint-specific. Push2 is primarily snapshot/list oriented; datacenter history and page-size caps vary by report. Do not assume one page size/history window applies to all Eastmoney datasets.

## Freshness and publication timing
Market snapshots are near-real-time vendor data; fundamental/flow/research datasets update on their own schedules. Freeze an `as_of`/retrieval time for cross-sectional work.

## Licensing and redistribution
Public availability does not establish commercial redistribution rights. Treat vendor-derived fields, research/news and commercial use as terms-sensitive; verify current Eastmoney rights before external redistribution.

## Data-quality limitations
Many fields are vendor-derived rather than official raw facts. Field IDs (`f*`), report schemas and security-market IDs can change. Cross-check important values with exchanges/official filings or a licensed source.

## Copy guidance
Primary reference: `../references/source-recipes/eastmoney.md`; verified toolkit: `../scripts/financial_data/eastmoney.py`. Freeze report name, field map, page size, throttle, retry/backoff, market-ID mapping, fallback and a small response fixture.