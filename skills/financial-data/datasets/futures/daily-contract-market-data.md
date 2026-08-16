# Dataset: 国内期货真实合约日行情 / 结算

## What this dataset means
SHFE/INE/DCE/CZCE/CFFEX/GFEX 的具体挂牌合约日级 OHLC、close、settlement、pre-settlement、成交量、成交额和OI。

## Common analytical uses
主力识别、期限结构、跨期、basis、成交/OI变化、回测和结算口径分析。

## Minimum canonical fields
`contract_id, variety, exchange, trade_date, delivery_month, open, high, low, close, settlement, pre_settlement, volume, turnover, open_interest, currency, units, source_url`。

## Frequency and timing semantics
按交易所 trading day；夜盘归属不能用本机自然日替代。收盘后数据发布时间各所不同。

## Recommended sources
对应交易所官方：`../../providers/shfe.md`, `../../providers/ine.md`, `../../providers/dce.md`, `../../providers/czce.md`, `../../providers/cffex.md`, `../../providers/gfex.md`。

## Alternatives / licensed alternatives
Wind/Choice/Tushare/其他授权期货数据；生产级实时优先券商/CTP或授权vendor。

## Methodology and unit caveats
exact、dominant、continuous 不同；close/settlement/pre-settlement分开；跨所 turnover/乘数/币种先统一。

## Source-selection pitfalls
交易所历史文件格式和路径可能分 regime；网页可访问不代表机器接口永久稳定。

## Provider cards
按合约所属交易所只读一个对应 provider 卡。

## Copy-ready references
`../../references/futures-ready-core.md`; verified reference `../../scripts/financial_data/cn_futures_official.py`。