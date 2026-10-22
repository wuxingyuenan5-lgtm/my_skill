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
按使用场景选择，而不是设一个全局固定首选：

- 无 Key、轻量研究或独立交叉核对：优先 shortlist `../../providers/tencent.md`，必要时比较 `../../providers/sina.md`、`../../providers/eastmoney.md`。
- 需要稳定结构化 A 股 API、Agent/自动化接入或与财务/估值/板块数据统一访问：shortlist `../../providers/hithink-finance.md`。
- 全市场、长历史批量研究：优先评估 HiThink market dump（Parquet）后本地查询，不要逐股调用历史接口。
- 机构生产/PIT需求：可考虑 `../../providers/wind-choice.md` 或其他授权源。

HiThink 当前公开能力不覆盖分钟 K/tick/Level-2；这些需求继续走券商/授权行情或其他明确支持的来源。

## Alternatives / licensed alternatives
mootdx/券商行情、Wind、Choice及其他授权源。

## Methodology and unit caveats
qfq/hfq/none 不可混用；复权价不是历史真实成交价，成交额不要由复权价格×成交量重建。确认 volume/amount 单位。

大批量 market dump 需要同时冻结数据文件的 retrieval time、校验信息和复权事件版本；短期预签名下载 URL 不能当作持久数据地址。

## Source-selection pitfalls
公共网页接口可能改字段、限流或缺正式SLA；分钟历史深度往往小于日线。结构化供应商 API 也不等于交易所 source of record，且账号权限、动态限流和再分发权需要单独验证。

## Provider cards
`../../providers/tencent.md`, `../../providers/hithink-finance.md`, `../../providers/eastmoney.md`, `../../providers/sina.md`, `../../providers/wind-choice.md`。

## Copy-ready references
`../../references/a-share-market-data.md`, `../../references/source-recipes/hithink-finance.md`; verified Tencent reference: `../../scripts/financial_data/adapters/tencent.py`。