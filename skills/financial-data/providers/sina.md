# Provider: Sina Finance public-web endpoints

last_verified: 2026-08-16

## Identity
Public-web financial quote source used mainly as a lightweight independent fallback for China market research. It is not treated as an exchange source of record or a formally supported public API.

## Access and authentication
Reference quote endpoints may work without API key; referer/header requirements are endpoint-dependent. Official API/auth contract for these web endpoints: unknown.

## Technical request limits
Official published QPS/RPM/concurrency limit: **unknown**. Recommended operating behavior is empirical: low concurrency, cache responses, batch symbols when supported, and back off on blocking or malformed responses.

## Data-range limits
Dataset and history depth are endpoint-dependent. The Skill primarily treats Sina as a quote/fallback source rather than a complete point-in-time historical database.

## Freshness and publication timing
Quotes are near-real-time public-web data with no SLA asserted here. Daily research should freeze a consistent cutoff and independently validate important fields.

## Licensing and redistribution
Research convenience only; public access does not imply commercial redistribution rights. Verify current Sina/site and underlying exchange-data terms.

## Data-quality limitations
Symbol prefixes, encoding, field order and unit semantics must be frozen. Use an independent source for material production decisions.

## Copy guidance
See `../references/source-recipes/tencent-sina-mootdx.md` and reference adapter `../scripts/financial_data/adapters/sina.py`. Freeze endpoint, symbol convention, field order, encoding, unit validation and fallback.