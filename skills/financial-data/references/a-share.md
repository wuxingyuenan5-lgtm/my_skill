# A-share Data Notes

## v0.1.0 executable quote path

**Tencent** is the primary CN quote adapter; **Sina** is an independent quote/price fallback.

Tencent mapped fields (provider indexes reviewed from the reference project):

| Index | Normalized meaning | Source unit | Internal unit |
|---|---|---|---|
| 3 | price | CNY | CNY |
| 4 | previous close | CNY | CNY |
| 5 | open | CNY | CNY |
| 32 | change % | percentage points | decimal |
| 33/34 | high/low | CNY | CNY |
| 37 | turnover amount | 万 CNY | CNY |
| 38 | turnover rate | percentage points | decimal |
| 39 | PE TTM | ratio | ratio |
| 44 | float market cap | 亿 CNY | CNY |
| 45 | total market cap | 亿 CNY | CNY |
| 46 | PB | ratio | ratio |
| 52 | static PE | ratio | ratio |

The float/total market-cap ordering is easy to reverse; adapters keep provider indexes isolated and tested.

## Stale quotes

A provider can return HTTP 200 with a frozen quote. Tencent points with zero turnover and price equal to previous close are flagged stale; context such as pre-open/halts must be considered before interpreting the flag.

## BSE

Do not silently use legacy 43/83/87/88 identifiers that may have migrated to `920xxx`. Resolve the current `.BJ` code.

## Future/registry capabilities

Eastmoney is modeled for exclusive fields such as margin financing, block trades, shareholder counts, fund flow, sector data and limit-state data; CNINFO/SSE/SZSE are modeled for first-party disclosures/market rules. These are registry/reference-only until adapters/tests are added.

Official industry taxonomy (e.g. 申万2021) and vendor concept tags must remain separate semantic fields; concept membership is not equivalent to a standardized industry classification.
