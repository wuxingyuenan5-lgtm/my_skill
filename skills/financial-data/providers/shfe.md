# Provider: SHFE / 上海期货交易所

last_verified: 2026-08-16

## Identity
Official source of record for SHFE public daily statistics and rules. Current official pages expose 日交易快讯、日交易排名、每日结算参数、仓单日报、库存周报等.

## Access and authentication
Public statistical pages/files generally require no account for ordinary browsing/download. Exact machine endpoint contract is not published as a stable API SLA. WAF/rate controls may change; never bypass them.

## Technical request limits
Official published QPS/RPM/concurrency limit for public statistical downloads: **unknown**. Recommended operating behavior: one/few cached requests per dataset/trading day, no high-concurrency crawling, exponential backoff on failures.

## Data-range limits
Daily and historical coverage varies by report; file/request format has changed across historical regimes. Freeze only the date regimes actually required by the project.

## Freshness and publication timing
Daily reports are generated after trading/settlement processing; exact machine-file SLA is not asserted. Collect after the exchange has completed the relevant report and keep a project-local `last_verified` smoke check.

## Licensing and redistribution
Official public data is suitable as research source of record, but website use statements and market-data redistribution/licensing rules still apply. Verify current SHFE information-management terms before commercial redistribution.

## Data-quality limitations
`close`, `settlement`, `pre_settlement`, volume, turnover and OI remain distinct. Member rankings can be subject to disclosure rules; an empty ranking is not automatically a source failure.

## Copy guidance
Daily reference: `../references/futures-ready-core.md`, runtime `../scripts/financial_data/cn_futures_official.py`; positioning: `../references/futures-positioning-ready-core.md`, runtime `../scripts/financial_data/futures_positioning.py`. Freeze report type, URL family, date regime, field/unit map, raw fixture and fallback.