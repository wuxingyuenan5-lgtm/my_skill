# Macro and Rates

## US Treasury — executable v0.1.0

The adapter parses the official daily Treasury yield-curve CSV and normalizes quoted percentages to decimals.

Normalized fields include available tenors such as 1M/3M/6M/1Y/2Y/5Y/10Y/20Y/30Y. Dedicated requests expose `yield_2y`, `yield_10y`, `yield_curve`, and locally derived `spread_10y_2y`.

Example internal values:

```text
4.37% yield -> 0.0437
10Y 4.71% - 2Y 4.37% -> 0.0034
```

The spread records both source tenors in `derived_from` and an algorithm version.

## Missing maturities

Do not interpolate silently. A curve with a missing requested maturity returns partial-data/error semantics rather than fabricating a point.

## CFTC

CFTC COT/positioning is registered as an official source but does not have an executable v0.1.0 adapter. When implemented, contract identity, report date, trader category and unit must be explicit.

## Macro releases

Future macro adapters must distinguish observation period, release/publish date, revision/vintage and retrieval date. Backtests should use the vintage available at the decision time, not a subsequently revised value.
