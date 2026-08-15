# Derivatives

Options/Greeks sources are registry/reference-only in v0.1.0; the schema is reserved so future adapters do not require a redesign.

## Option contract identity

Record underlying, exchange, expiry, call/put, strike, contract multiplier, exercise style if material, and exact contract symbol.

## Core fields

- bid / ask / last
- volume (`contracts`)
- open interest (`contracts`)
- implied volatility as decimal
- delta / gamma / vega / theta / rho
- underlying spot/reference time

Greeks/IV may be provider/exchange-computed or locally derived; record which. Different model assumptions are not automatically comparable.

## 0DTE and timezone

“0DTE” means expiry on the current **exchange-local trading date**, not simply UTC date. US options must respect America/New_York DST transitions.

## Flow signals

Metrics such as volume/open-interest ratio, put/call ratios, IV skew or net delta exposure are **derived signals**, not facts about trader intent. Store raw volume/OI separately and attach calculation parameters/version.

## Compliance

CBOE is modeled as an authoritative US options source but licensing/approval constraints apply; it is not enabled by default in v0.1.0. Yahoo options are also registry-only and subject to its usage terms.
