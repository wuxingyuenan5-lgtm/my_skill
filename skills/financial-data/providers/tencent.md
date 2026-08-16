# Provider: Tencent Finance public-web endpoints

last_verified: 2026-08-16

## Identity
Public-web market-data source used for research integration, especially A-share quotes/K-lines. It is not treated here as a formally supported public market-data API with an SLA. Best for lightweight CN quote/K-line work; poor fit for licensed redistribution or high-concurrency production.

## Access and authentication
Current reference quote/K-line endpoints do not require an API key. Header/referer behavior is endpoint-dependent. Official automation/auth contract: unknown. Do not bypass access controls.

## Technical request limits
Official published QPS/RPM/concurrency limit: **unknown**. Recommended operating limit: empirical/conservative — prefer serial or small batches, cache results, back off on blocking/HTTP errors; no numeric recommendation is represented as official.

## Data-range limits
K-line coverage in the reference implementation spans intraday through monthly resolutions, but lookback depth is endpoint/resolution dependent. Minute-history retention should be verified in the downstream project before relying on long backfills.

## Freshness and publication timing
Quotes are near-real-time public-web data; exact exchange latency/SLA is not committed here. Daily bars are suitable after the trading session is complete. Keep project-local smoke checks for field changes.

## Licensing and redistribution
Research integration convenience only. Commercial use, redistribution and derived-data rights are **not inferred** from public accessibility; verify current Tencent/site terms and any underlying exchange market-data rights.

## Data-quality limitations
Confirm symbol mapping, adjustment mode, volume/amount units and suspension behavior. qfq/hfq/none must not be mixed; adjusted prices are not historical traded prices.

## Reference endpoints (verified 2026-08-16 against Vibe-Research app.py)

- Daily/weekly/monthly (qfq/hfq/none): `GET https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={key},{resolution},,,{count},{adjustment}` — e.g. `sh600519,day,,,180,qfq`; symbol prefix `sh/sz/bj`; response rows `[date, open, close, high, low, volume, ...]`, `qfq{period}` key.
- Minute (m1/m5/m15/m30/m60, unadjusted): `GET https://ifzq.gtimg.cn/appstock/app/kline/mkline?param={key},m60,,{count}`.
- Quote text (GBK-encoded `~`-delimited fields): `GET https://qt.gtimg.cn/q={key}` — field map: 3=price, 4=prev_close, 5=open, 31=change, 32=change_pct, 33=high, 34=low, 37=turnover(万), 38=turnover_rate, 39=pe_ttm, 44=float_mcap(亿), 45=mcap(亿), 46=pb, 47/48=limit up/down, 49=volume_ratio, 52=pe_static.
- **CN-direct connectivity**: build request with `urllib.request.ProxyHandler({})` to bypass system proxy for these CN endpoints (verified in production); keep `User-Agent: Mozilla/5.0` and low concurrency.

## Copy guidance
Primary references: `../references/a-share-market-data.md`, `../references/source-recipes/tencent-sina-mootdx.md`; verified reference implementation: `../scripts/financial_data/adapters/tencent.py`. Freeze endpoint family, field map, adjustment rule, unit checks, fallback and `last_verified` into the downstream project.