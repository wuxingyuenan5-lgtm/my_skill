# A股市场宽度 / 横截面研究

## Objective
支持全A涨跌家数、成交额、百亿成交股、市场中位数、行业扩散度、集中度等横截面研究。

## Required datasets
- `../datasets/cn-equity/market-cross-section.md`
- 若按行业统计：`../datasets/cn-equity/industry-classification.md`

## Optional datasets
- `../datasets/cn-equity/kline.md`：需要历史宽度回放或连续时间序列时才读。
- `../references/a-share-microstructure.md`：涨停/炸板/跌停等情绪池。

## Recommended source path
横截面优先看 Eastmoney 数据卡；研究口径需额外核对交易所/专业源。行业归属需明确申万版本或自定义分类。

## Methodology / caveats
成交额、总市值/流通市值、上涨家数的股票宇宙必须固定定义；ST/退市整理/北交所是否纳入要写清。行业分类必须带 taxonomy/version/effective date。

## What to freeze into the downstream project
市场宇宙定义、横截面字段表、行业映射、成交额单位、更新时间、异常值/停牌处理、source provenance。

## Avoid unnecessary reads
无需扫描所有A股基本面、SEC、期货或宏观 Provider。