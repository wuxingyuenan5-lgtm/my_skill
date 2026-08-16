# Provider: CNINFO / 巨潮资讯

last_verified: 2026-08-16

## Identity
Official Chinese listed-company disclosure platform and a key source for announcements/filings. The current site also exposes separate Data Platform/Data API/commercial data-service entrypoints. For issuer disclosures, CNINFO is preferred over vendor summaries.

## Access and authentication
Public announcement search/browsing is accessible through the website; login exists for user features. Authentication/entitlement for the separate Data API/service products is contract/product dependent. Do not assume public web search and commercial Data API have the same rights or limits.

## Technical request limits
Official public-web QPS/RPM/concurrency limit: **unknown**. Data API product quotas: **account/contract dependent; not publicly frozen here**. Use targeted searches, pagination and caching; do not crawl aggressively or bypass access controls.

## Data-range limits
Announcement history is broad but query pagination/date limits are endpoint-specific. `orgId`/security identity mappings should be cached rather than rediscovered per request.

## Freshness and publication timing
Event-driven. Preserve announcement publish time, filing period and retrieval time. New disclosures can appear throughout the trading/non-trading day.

## Licensing and redistribution
Filings are public disclosures, but bulk data services, redistribution and commercial API use can carry separate terms. Verify current CNINFO/market-data terms before redistribution.

## Data-quality limitations
Use the original announcement/PDF as source of record; search metadata and extracted text can be incomplete. Keep announcement ID, orgId, URL, publish time and file hash where reproducibility matters.

## Copy guidance
See `../references/a-share-fundamentals.md`, `../references/a-share-research-news.md`, `../references/source-recipes/cninfo-exchanges-ths.md`. Freeze orgId lookup, query filters, pagination, publish-time semantics, attachment handling and local caching.