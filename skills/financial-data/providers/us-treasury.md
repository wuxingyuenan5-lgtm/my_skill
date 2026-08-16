# Provider: U.S. Department of the Treasury interest-rate feeds

last_verified: 2026-08-16
official_reference: https://home.treasury.gov/treasury-daily-interest-rate-xml-feed

## Identity
Official source of record for Treasury daily par yield curves, bill rates, real yield curves and related daily interest-rate statistics.

## Access and authentication
Official XML feed uses HTTP GET and requires no API key in the documented feed.

## Technical request limits
Official QPS/RPM/concurrency limit on the documented XML page: **not stated**. For `field_tdr_date_value=all`, pagination is zero-based and the feed returns **300 rows by default per page**. Prefer year/month queries or cached sequential pagination rather than repeatedly requesting all history.

## Data-range limits
Official documented availability: Daily Treasury Par Yield Curve Rates from **1990**; Bill Rates from 2002; Long-Term Rates from 2000; Real Yield Curve from 2003; Real Long-Term Rates from 2000.

## Freshness and publication timing
Daily curve statistics are based on indicative secondary-market quotations around the close methodology; they are not real-time tradable bond quotes. Preserve observation date and retrieval time.

## Licensing and redistribution
Official U.S. government source; use attribution and verify terms for any third-party redistribution package, but no paid entitlement is required for the documented public feed.

## Data-quality limitations
Series methodology has changed historically (for example the 2021 curve-method change). Tenor availability also has historical breaks; do not fabricate missing tenors.

## Copy guidance
See `../datasets/macro/us-rates-treasury.md`, `../references/macro-rates.md`; verified adapter `../scripts/financial_data/adapters/treasury.py`. Freeze endpoint/data key, date query, tenor map, percent-unit handling and historical methodology notes.