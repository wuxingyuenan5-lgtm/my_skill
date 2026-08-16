# Provider: Wind / Choice professional data

last_verified: 2026-08-16

## Identity
Licensed professional financial-data terminals/APIs with broad China/global coverage. Suitable when project requirements need stable identifiers, PIT history, institutional datasets or commercial support unavailable from public-web sources.

## Access and authentication
Paid license/entitlement and installed client/API credentials are normally required. Available datasets and API permissions depend on the user's contract, terminal and organization.

## Technical request limits
Public universal QPS/RPM/concurrency limit: **not applicable / unknown**. Quotas, row limits and concurrency are license/API/account dependent. Read the account's current vendor documentation and error codes rather than copying a generic number into every project.

## Data-range limits
Coverage/history varies by product and entitlement. Professional access can be broad, but a terminal license does not imply every API dataset or redistribution right is enabled.

## Freshness and publication timing
Dataset-specific, from real-time market data to periodic fundamentals/research. Preserve vendor timestamp/as-of and distinguish exchange raw vs vendor standardized fields.

## Licensing and redistribution
Strictly licensed. External redistribution, derived-data distribution, server deployment and sharing credentials/data can require additional rights. Treat contract/vendor documentation as controlling.

## Data-quality limitations
Vendor normalization is valuable but still methodology-dependent; field definitions, industry taxonomies, consensus and adjusted data require dictionary/version capture. Cross-check critical official facts where possible.

## Copy guidance
See `../references/professional-data-sources.md`. Downstream project should freeze dataset/field codes, entitlement assumptions, unit/currency, PIT semantics, vendor-version notes and a non-secret credential configuration pattern.