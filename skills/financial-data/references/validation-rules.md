# Validation Rules

## Evidence tiers

- **Tier 1 — authoritative simple facts:** exchange/regulator/government publications. One authoritative source can pass when the field and timestamp are clear.
- **Tier 2 — provider-derived fields:** valuation, classifications, fund-flow buckets, vendor estimates. Cross-check when the value is decision-relevant or providers use different conventions.
- **Tier 3 — anomalies / major conclusions:** unusual values, high-impact research claims, or disputed numbers. Require an independent source or return unresolved uncertainty.

## Structural checks

- provenance fields present
- numeric type and sensible range
- currency/unit compatibility
- OHLC invariant: high >= open/close/low and low <= open/close/high
- volume/turnover non-negative
- time series ordered and non-duplicated
- explicit timezone for timestamps
- stale provider timestamp/status surfaced
- price-adjustment convention consistent across history

## Cross-source comparison

Normalize unit, currency convention and percentage scale before comparison. Default comparable numeric tolerance is conservative (`rel_tol=0.5%` unless field-specific logic overrides it).

If two comparable observations exceed tolerance:

1. retain the primary observation;
2. attach `SOURCE_CONFLICT` quality flag;
3. include the secondary source/value/timestamp in diagnostics;
4. do not average the values automatically;
5. investigate likely time, adjustment, denominator, vendor-estimate or definition differences.

A conflict is information. It must not disappear merely to produce a neat answer.
