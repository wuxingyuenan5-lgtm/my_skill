# Funds and ETF Data Handbook

## Datasets

NAV/IOPV, market price, premium-discount, AUM/shares outstanding, holdings, creation/redemption/flows, distributions, index benchmark, fees, manager/style, corporate actions.

## China

Exchange/issuer/fund-company disclosures are definition/holdings sources. For broad normalized public-fund API access, HiThink Financial API can cover profiles, managers/companies, NAV/returns, drawdowns/performance indicators, disclosed stock/bond holdings, industry/asset allocation, holders, dividends, fund financials and ETF/LOF market data. Wind/Choice and other licensed vendors remain alternatives for institution-grade history and cross-vendor normalization.

For ETF market price/turnover use exchange/market-data sources, not a NAV source. Do not treat HiThink manager/style/diagnostic labels as source-of-record facts when they are vendor-derived.

Detailed dataset card: `../datasets/funds/cn-public-funds.md`; provider card: `../providers/hithink-finance.md`.

## US/global

Issuer websites and exchange filings are primary for holdings/fees/distributions; market quote source handles price. ETF flow is usually derived from shares outstanding × NAV/price changes and provider methodologies can differ—record method.

## Common mistakes

- market price != NAV/IOPV;
- AUM != market capitalization of listed units in all contexts;
- holdings disclosure has publication lag;
- leveraged/inverse ETF daily objective must be recorded;
- futures-based commodity ETFs need underlying roll methodology;
- current manager/holdings snapshots must not be retroactively applied to historical decision dates.
