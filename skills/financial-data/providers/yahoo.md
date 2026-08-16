# Provider: Yahoo Finance

last_verified: 2026-08-16

## Identity
Global financial website/vendor. The Skill uses Yahoo v8 Chart public-web endpoints as a research convenience for US/HK K-lines; these endpoints are **not treated as a formally supported public market-data API with an SLA**.

## Access and authentication
The current v8 Chart reference path works without cookie/crumb for the supported K-line workflow. Other Yahoo endpoint families may require cookies/crumb/login or premium access. Do not generalize v8 behavior to all Yahoo data.

## Technical request limits
Official published QPS/RPM/concurrency limit for the v8 Chart web endpoint: **unknown**. Use caching, low concurrency and backoff; a public web response is not a production SLA.

## Data-range limits
Daily history is broad; intraday lookback is more limited and endpoint-dependent. Yahoo Finance premium products advertise longer exportable history/features, but those subscription entitlements are separate from the v8 reference endpoint.

## Freshness and publication timing
Market data latency can vary by venue/instrument and product tier. Preserve exchange/timezone and do not assume every quote is exchange-real-time.

## Licensing and redistribution
Research convenience only for the public-web integration. Commercial use/redistribution and premium export rights are governed by Yahoo and underlying exchange/data-provider terms; verify before external redistribution.

## Data-quality limitations
Keep `close` and `adjclose` distinct; handle splits/dividends, null bars, timezone and symbol/venue suffixes. Cross-check critical prices with an exchange/authorized feed.

## Copy guidance
See `../references/global-equity-market-data.md`, `../references/source-recipes/sec-yahoo-us-providers.md`; verified adapter `../scripts/financial_data/adapters/yahoo_chart.py`. Freeze interval/range assumptions, timezone, adjustment/null rules, retry and fallback.