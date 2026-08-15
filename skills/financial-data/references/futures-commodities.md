# Futures and Commodities

No production futures/commodity source adapter ships in v0.1.0. This reference defines the contract for later adapters.

## Identity

A futures observation must identify:

- exchange
- root/commodity
- exact contract month/year (`contract_id`)
- quote currency and price unit
- contract multiplier where needed
- session/trading date

A continuous series is a **derived instrument**, not a real tradable contract. It must include roll rule, adjustment method and roll calendar/version.

## Session semantics

Night sessions can belong to the next exchange trading day even when the wall-clock calendar date is the prior evening. Preserve timezone and exchange trading-date rules.

## Common fields

OHLC, settlement, volume (`contracts`), open interest, basis/spread, limit state, delivery/expiry metadata. Do not mix last trade and settlement as interchangeable close prices.

## Cross-market commodities

LME/COMEX/SHFE prices may differ by currency, contract specification, tax/duty, delivery location and trading hours. Convert units/currency explicitly before interpreting a spread.

## Continuous/backtest safety

Never build returns by naively concatenating contract prices across roll gaps. State whether series is raw splice, ratio-adjusted, difference-adjusted, or total-return style.
