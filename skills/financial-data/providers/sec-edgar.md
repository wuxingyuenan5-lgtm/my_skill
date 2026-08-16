# Provider: SEC EDGAR

last_verified: 2026-08-16
official_reference: https://www.sec.gov/about/developer-resources

## Identity
U.S. SEC official source of record for EDGAR filings, submissions, XBRL companyfacts/frames and filing indexes.

## Access and authentication
Public EDGAR data requires no API key. Automated requests must declare a descriptive User-Agent identifying the organization/application and contact information; unclassified bots outside acceptable policy can be managed/blocked.

## Technical request limits
**Official current maximum: 10 requests/second total per user/IP policy, regardless of number of machines.** SEC asks users to download only what is needed and moderate requests. Exceeding policy can cause temporary IP limiting. Conservative project practice: stay below the maximum, cache submissions/companyfacts/indexes and avoid per-filing repeated downloads.

## Data-range limits
Filings/index archives have long historical coverage; availability differs by filing/data product. Companyfacts is a current API view and can reflect later amendments, so it is not by itself a historical point-in-time snapshot.

## Freshness and publication timing
SEC notes filings are often available on sec.gov within roughly 1-3 minutes of the EDGAR system timestamp. Preserve accepted/filed/available times for event studies.

## Licensing and redistribution
Official public U.S. government disclosure data is broadly accessible; still preserve filing attribution and review any third-party exhibit/copyright issues in attachments or commercial repackaging.

## Data-quality limitations
XBRL concepts, issuer extensions, units, frames and amendments require normalization. Do not use today's companyfacts response as if every value was known historically.

## Copy guidance
See `../datasets/global-equity/sec-filings-companyfacts.md`, `../references/sec-edgar-advanced.md`; runtimes `../scripts/financial_data/adapters/sec_edgar.py`, `../scripts/financial_data/sec_official.py`. Freeze User-Agent/contact, CIK map, caching, PIT rules and 10 req/s ceiling.