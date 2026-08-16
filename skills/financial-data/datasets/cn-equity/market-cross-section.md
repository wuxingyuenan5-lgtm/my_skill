# Dataset: A股市场横截面

## What this dataset means
在同一 as-of 时点获取全市场证券列表及价格、涨跌幅、成交额、市值等横截面字段。

## Common analytical uses
涨跌家数、市场中位数、百亿成交股、宽度、集中度、风格/行业统计和股票池筛选。

## Minimum canonical fields
`instrument_id, name, as_of, last/close, change_pct, volume, amount, market_cap/free_float_cap, listing_status, source_id`；行业字段应另带taxonomy版本。

## Frequency and timing semantics
盘中横截面是近实时快照；收盘统计要冻结统一截止时点，避免跨证券更新时间不一致。

## Recommended sources
研究型全市场列表/快照优先 `../../providers/eastmoney.md`；独立报价核对可用 Tencent/Sina；机构生产可用 Wind/Choice。

## Alternatives / licensed alternatives
交易所证券列表 + 独立行情源、Wind、Choice。

## Methodology and unit caveats
股票宇宙必须声明是否含北交所、ST、退市整理、停牌；成交额和市值单位统一后再汇总。

## Source-selection pitfalls
vendor横截面字段可能是派生值；不同源的流通市值、涨跌幅基准、证券状态定义可能不同。

## Provider cards
`../../providers/eastmoney.md`, `../../providers/tencent.md`, `../../providers/sina.md`, `../../providers/wind-choice.md`。

## Copy-ready references
`../../references/a-share-market-data.md`, `../../references/a-share-microstructure.md`; reference toolkit `../../scripts/financial_data/eastmoney.py`。