# Provider: INE / 上海国际能源交易中心

last_verified: 2026-08-16

## Identity
Official source of record for INE products. Current official site exposes 日交易快讯、日交易排名、每日结算参数、仓单日报、库存周报等; the daily/weekly page states filtered daily data is generated after close/settlement completes.

## Access and authentication
Ordinary official pages are public, but the site can present WAF/challenge behavior to automated clients. Daily market-data machine path is frozen in the reference runtime; **member-positioning machine transport is intentionally not marked READY** even though the official ranking page exists.

## Technical request limits
Official published QPS/RPM/concurrency limit: **unknown**. Use low-frequency cached retrieval after settlement; back off on WAF/403 and do not attempt CAPTCHA/access-control bypass.

## Data-range limits
Dataset-specific and historical path regimes can differ. Do not infer a ranking machine URL from SHFE string substitution; verify each current INE report family independently.

## Freshness and publication timing
Official daily page: data is produced after market close and settlement completion. Exact machine-file timestamp is not treated as a guaranteed SLA.

## Licensing and redistribution
Official public facts are appropriate research sources; redistribution/commercial market-data rights require current INE/SHFE information-management review.

## Data-quality limitations
BC/SC/LU/NR/SCFIS product conventions, trading day/night session, settlement and units must be preserved. Ranking non-publication and source blocking are different states.

## Copy guidance
Daily: `../references/futures-ready-core.md`; positioning caveat: `../references/futures-positioning-ready-core.md`. Freeze exact INE source URL, report regime, WAF-safe failure handling, fields/units and `last_verified`; do not promote ranking fetch to READY until a current stable transport is verified.