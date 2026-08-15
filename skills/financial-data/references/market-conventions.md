# Market Conventions

## Time

Use timezone-aware timestamps. Trading-session date and natural date are different concepts; night-session futures are especially sensitive to this distinction.

For point-in-time research, use when information became public (`publish_date` / filing `as_of`), not only the accounting period end.

## Percentages

Internal decimal convention:

- 3.21% → `0.0321`
- 50 bp → `0.005`

Formatting as `%` happens only at presentation.

## Price series

Historical prices identify `raw`, `forward_adjusted`, `backward_adjusted`, or `total_return_adjusted`. Returns spanning corporate actions must use a consistent convention.

## Quantity units

Never use generic “volume” without knowing the unit. Normalize/label `shares`, `lots`, `contracts`, currency amount, or provider-specific count. A-share turnover rate is volume shares / explicit free-float shares; market cap is not a substitute denominator.

## Currency

Store both `unit` and `currency` where meaningful. Do not infer currency from ticker or magnitude after cross-market joins; use instrument/source metadata.

## Missing data

`None`/absent means unavailable. Zero means a measured zero. Provider HTTP success with an empty or frozen payload can still be stale/unavailable and requires validation.
