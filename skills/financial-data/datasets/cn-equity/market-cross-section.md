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
按规模和用途路由：

- 无 Key、研究型盘中/收盘横截面：优先 `../../providers/eastmoney.md`，独立报价核对可用 Tencent/Sina。
- 需要结构化 API/Agent 访问的 A 股快照、标的目录、指数/板块成分：可 shortlist `../../providers/hithink-finance.md`。
- 需要全市场长历史面板：优先评估 HiThink market dump → Parquet/DuckDB，本地计算横截面；避免逐股远程抓取。
- 机构生产/PIT需求：Wind/Choice 或其他授权源。

## Alternatives / licensed alternatives
交易所证券列表 + 独立行情源、Wind、Choice。

## Methodology and unit caveats
股票宇宙必须声明是否含北交所、ST、退市整理、停牌；成交额和市值单位统一后再汇总。

若横截面来自历史文件，必须使用该交易日可获得的证券状态、成分/行业版本；不要用今天的股票池或板块成分回填历史。

## Source-selection pitfalls
vendor横截面字段可能是派生值；不同源的流通市值、涨跌幅基准、证券状态定义可能不同。HiThink 的 THS 概念/行业板块属于 vendor taxonomy，不应与申万/中信/交易所分类无条件等同。

## Provider cards
`../../providers/hithink-finance.md`, `../../providers/eastmoney.md`, `../../providers/tencent.md`, `../../providers/sina.md`, `../../providers/wind-choice.md`。

## Copy-ready references
`../../references/a-share-market-data.md`, `../../references/a-share-microstructure.md`, `../../references/source-recipes/hithink-finance.md`; Eastmoney reference toolkit `../../scripts/financial_data/eastmoney.py`。