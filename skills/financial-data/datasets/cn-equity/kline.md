# Dataset: 中国股票 K线

## What this dataset means
单一证券在明确时间周期上的 OHLC、成交量/成交额及可选复权价格序列。

## Common analytical uses
技术指标、趋势/均线、收益率、波动率、事件窗口、回测。

## Minimum canonical fields
`instrument_id, trade_date/time, open, high, low, close, volume, amount, adjustment, source_id, retrieved_at`。

## Frequency and timing semantics
日线按交易所交易日；分钟线必须带时区/session。停牌日可能缺bar，不能自动当零成交bar。

## Recommended sources
研究型A股历史K线优先 shortlist `../../providers/tencent.md`；横截面/补充可比较 `../../providers/eastmoney.md`、`../../providers/sina.md`。机构生产/PIT需求可考虑 `../../providers/wind-choice.md`。

## Alternatives / licensed alternatives
mootdx/券商行情、Wind、Choice及其他授权源。

## Methodology and unit caveats
qfq/hfq/none 不可混用；复权价不是历史真实成交价，成交额不要由复权价格×成交量重建。确认 volume/amount 单位。

## Source-selection pitfalls
公共网页接口可能改字段、限流或缺正式SLA；分钟历史深度往往小于日线。

## Provider cards
`../../providers/tencent.md`, `../../providers/eastmoney.md`, `../../providers/sina.md`, `../../providers/wind-choice.md`。

## Copy-ready references
`../../references/a-share-market-data.md`; verified reference: `../../scripts/financial_data/adapters/tencent.py`。