# Dataset: CFTC COT 持仓

## What this dataset means
CFTC Commitments of Traders 报告中的期货/期权持仓分类统计，不是逐账户或实时头寸。

## Common analytical uses
投机/商业持仓、净头寸、极值、拥挤度和宏观商品定位。

## Minimum canonical fields
`report_date, publication_date, market_code/name, contract_units, participant_category, long, short, spreading, open_interest, source_id`。

## Frequency and timing semantics
周频；报告对应的持仓日期与公开发布日期不同，必须同时保存。

## Recommended sources
`../../providers/cftc.md`。

## Alternatives / licensed alternatives
授权vendor可提供映射和历史整理，但category定义仍以CFTC为准。

## Methodology and unit caveats
Legacy/Disaggregated/TFF等报告分类不同；净多=long-short是分类口径派生，不可跨report family直接拼接。

## Source-selection pitfalls
市场代码映射、报告family、futures-only vs futures-and-options combined容易混淆。

## Provider cards
`../../providers/cftc.md`。

## Copy-ready references
`../../references/macro-positioning-events.md`; verified helper `../../scripts/financial_data/cftc.py`。