# Provider: GFEX / 广州期货交易所

last_verified: 2026-08-16

## Identity
Official source of record for GFEX products such as lithium carbonate and polysilicon. Current product pages expose 日行情、仓单日报、日成交持仓排名 and contract/rule notices.

## Access and authentication
Current public statistics request families used by the reference implementation require no API key. They are public web interfaces, not a versioned public API SLA.

## Technical request limits
Official published QPS/RPM/concurrency limit: **unknown**. Prefer one batch daily request plus the minimum required ranking contract requests; cache results and back off on 403/429/5xx.

## Data-range limits
GFEX is a newer exchange; dataset start dates differ by product/report. Position-ranking contract discovery and the three ranking types are separate request steps. Historical depth must be checked for the requested product.

## Freshness and publication timing
Daily market/ranking/warehouse reports are post-close; exact machine availability is not represented as guaranteed. Rule parameters can change via dated notices, so save effective dates.

## Licensing and redistribution
Official research source; commercial redistribution and行情 licensing require current GFEX terms. Product notices are authoritative for temporary fees/margins/opening limits.

## Data-quality limitations
Keep variety vs contract, settlement vs close, volume/OI units and product-specific contract parameters explicit. Do not use current LC fee/margin rules for historical backtests.

## Copy guidance
See `../references/futures-ready-core.md`, `../references/futures-positioning-ready-core.md`; reference runtimes `../scripts/financial_data/cn_futures_official.py`, `../scripts/financial_data/futures_positioning.py`. Freeze request form, contract discovery, field map, product specs, rule effective dates and fixtures.