# US / Hong Kong Notes

## US — SEC EDGAR

v0.1.0 supports:

- ticker → CIK lookup
- filing metadata (`10-K`, `10-Q`, `8-K`, etc.)
- XBRL company facts
- normalized revenue, net income, operating cash flow, assets, liabilities and R&D expense

`SEC_CONTACT` must identify the caller truthfully before network access. Filing/XBRL observations preserve filing date (`as_of`/publish evidence), report period, form, fiscal labels and taxonomy tag. This is essential for point-in-time/backtest safety.

US company facts can use multiple GAAP tags for economically similar metrics. The adapter uses an ordered tag map and retains the exact chosen tag; cross-sectional work must not assume all issuers use one tag.

## Hong Kong

Instrument normalization supports canonical numeric tickers such as `0700.HK`. Executable HK market-data adapters are not part of v0.1.0. Tencent/Sina/Yahoo/Eastmoney coverage remains registry/reference knowledge until implemented and tested.

## Restricted/registry sources

- Yahoo: broad research coverage, but usage constraints make it non-default for commercial workflows.
- CBOE: authoritative US options/Greeks data, but licensing/approval requirements apply.

Do not describe registry-only sources as implemented runtime capability.
