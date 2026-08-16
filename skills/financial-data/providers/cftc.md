# Provider: CFTC Public Reporting / Commitments of Traders

last_verified: 2026-08-16

## Identity
U.S. CFTC official source for COT datasets. Current Public Reporting Hub exposes dataset views and OData access for Disaggregated, TFF, Legacy/Supplemental families.

## Access and authentication
Public Data Hub/OData views are accessible without a CFTC account for ordinary public-data queries. No CFTC-specific API key requirement is frozen here.

## Technical request limits
Official CFTC-specific QPS/RPM/concurrency limit found on the dataset pages: **unknown**. Query only required columns/date ranges, cache weekly data and avoid repeated full-table scans. If the underlying reporting platform returns rate-limit errors, back off rather than treating them as no data.

## Data-range limits
History depends on report family and its creation date; current Data Hub includes filtered views and all-history datasets. Always record dataset identifier/report family rather than assuming one COT schema.

## Freshness and publication timing
COT is weekly. Preserve both the position/report date and the publication/update date; they are not the same event time.

## Licensing and redistribution
Official public U.S. government data; retain CFTC attribution and distinguish any vendor-enriched mappings from raw CFTC facts.

## Data-quality limitations
Legacy, Disaggregated, TFF, futures-only and futures+options-combined categories are not interchangeable. Filter carefully to avoid double counting in “All” views.

## Copy guidance
See `../datasets/macro/cftc-positioning.md`, `../references/macro-positioning-events.md`; reference helper `../scripts/financial_data/cftc.py`. Freeze dataset ID, report family, filters, publication-date semantics and category map.