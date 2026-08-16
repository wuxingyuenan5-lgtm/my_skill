# Dataset: 美国国债收益率 / 利率曲线

## What this dataset means
美国财政部官方公布的国债收益率曲线及相关期限数据；与实时可交易Treasury报价/期货并非同一数据产品。

## Common analytical uses
2Y/10Y、曲线斜率、宏观状态、跨资产估值与晨报。

## Minimum canonical fields
`observation_date, tenor, yield, unit, publication/source timestamp, source_id`。

## Frequency and timing semantics
通常按官方日度发布节奏使用；研究中保存observation date与retrieved_at，避免把后续修正/补发当成当时已知。

## Recommended sources
`../../providers/us-treasury.md`。

## Alternatives / licensed alternatives
FRED可做分发/历史便利层；实时可交易利率和Treasury报价使用授权市场数据源。

## Methodology and unit caveats
百分比/小数内部表达统一；不同曲线产品和期限定义不要混用。

## Source-selection pitfalls
官方日度曲线不是交易所实时收益率；API/CSV页面结构可能更新。

## Provider cards
`../../providers/us-treasury.md`。

## Copy-ready references
`../../references/macro-rates.md`; verified reference `../../scripts/financial_data/adapters/treasury.py`。