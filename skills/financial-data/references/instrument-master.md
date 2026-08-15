# Instrument Master

The resolver protects downstream analysis from symbol collision and stale identifiers.

## Canonical display forms

- A-share: `600519.SH`, `000001.SZ`, `920xxx.BJ`
- Hong Kong: `0700.HK` (numeric codes are zero-padded)
- US: `AAPL.US`, `BRK.B.US`
- Common index aliases: `SPX`, `NDX`, `DJI`, `HSI`
- US rates aliases: `UST2Y`, `UST10Y`, `UST30Y`, `USTCURVE`

Every resolved instrument carries canonical ID, exchange, country, currency and asset class.

## Ambiguity rules

1. Explicit suffix wins.
2. Bare six-digit A-share symbols use deterministic exchange rules, with a small explicit index map.
3. Bare `000001` means the Shenzhen equity `000001.SZ`; use explicit `000001.SH` for the SSE Composite. This avoids guessing based on context.
4. Bare short numeric HK codes are not guessed; provide `.HK` or `market="HK"`.
5. Alphabetic tickers default to US only when syntactically valid.
6. Company-name fuzzy search is intentionally outside v0.1.0. Return `INSTRUMENT_NOT_FOUND` rather than guess.

## BSE migration guard

Legacy Beijing Stock Exchange number ranges such as many `43/83/87/88xxxx` identifiers may have migrated to `920xxx`. A provider can still return HTTP 200 with stale/frozen data for an old code. v0.1.0 therefore rejects legacy-looking bare identifiers and requires the current `.BJ` ticker rather than auto-transforming them.

## Provider IDs

Provider IDs belong in `external_ids` (e.g. SEC CIK), not in the canonical ticker. Adapters translate canonical identity to provider syntax at their boundary.
