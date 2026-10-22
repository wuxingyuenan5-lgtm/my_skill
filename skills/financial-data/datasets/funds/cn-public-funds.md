# Dataset: 中国公募基金

## What this dataset means
Structured public-fund data covering product identity, managers/companies, NAV and returns, disclosed holdings/allocation, holders, distributions, selected financial statements/indicators and listed ETF/LOF market data.

Fund disclosure data and exchange-traded market-price data are different datasets and must remain separate.

## Common analytical uses
Fund screening, manager/product research, style and holdings analysis, asset-allocation monitoring, return/drawdown studies, ETF/LOF market-price research and FOF due diligence.

## Minimum canonical fields
Choose fields by sub-dataset. Common identity/provenance fields are:

`fund_id, fund_name, fund_type, report_date/as_of, published_at_if_known, currency, source_id, retrieved_at`.

For NAV/performance: `nav_date, unit_nav, accumulated_nav, return_period, return_value`.

For holdings/allocation: `report_date, holding_instrument_id, weight, market_value, asset_class/industry, disclosed_or_estimated`.

For managers: persist manager identity and effective start/end dates instead of only today's manager snapshot.

## Timing semantics
Holdings, holder structure and financial statements are periodic disclosures with publication lag. Backtests and historical manager/style analysis must use the version available at the historical decision date.

ETF/LOF market price is exchange market data; do not substitute NAV for tradable price or vice versa.

## Recommended sources
For a broad structured China public-fund API, shortlist `../../providers/hithink-finance.md`. Its current contract includes fund profiles, fund companies/managers, NAV/returns, drawdowns/performance indicators, stock/bond holdings, industry/asset allocation, holders, dividends, fund financials and ETF/LOF market data.

For source-of-record validation, prefer fund-company/issuer disclosures and exchange documents where the exact legal disclosure matters. Wind/Choice and other licensed vendors remain alternatives for institution-grade history and cross-vendor normalization.

## Methodology and unit caveats
- market price != NAV/IOPV;
- periodic disclosed holdings are not real-time portfolio positions;
- industry allocation depends on taxonomy/provider methodology;
- manager style/diagnostic labels are vendor-derived unless independently reproduced;
- return windows and annualization methods must be explicit;
- fund-of-funds, QDII, commodity, leveraged/inverse and derivatives-heavy products may require product-specific treatment.

## Source-selection pitfalls
Do not infer a historical holding from a later disclosure. Preserve report period, availability/publication date where possible and provider methodology for rankings/diagnostics.

## Provider cards
`../../providers/hithink-finance.md`, `../../providers/wind-choice.md`.

## Copy-ready references
`../../references/funds-etf.md`, `../../references/source-recipes/hithink-finance.md`.
