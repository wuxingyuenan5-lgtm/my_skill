# Dataset: 期货交易参数

## What this dataset means
交易所/期货公司按日期生效的保证金、涨跌停、手续费、交易时段、最小变动价位、合约乘数与交割规则。

## Common analytical uses
回测交易成本、杠杆/保证金、风控、夜盘session、合约规格和交割约束。

## Minimum canonical fields
`effective_date, exchange, contract/variety, multiplier, tick_size, price_limit, exchange_margin, broker_margin, fee_rule, session, delivery_rule, source_id`。

## Frequency and timing semantics
规则事件驱动且可能临时调整；必须按effective date保存历史版本。

## Recommended sources
交易所规则/通知是 exchange-level source of record；实际账户保证金和手续费以期货公司/账户约定为准。

## Alternatives / licensed alternatives
Wind/Choice和券商/期货公司API可做聚合，但需区分交易所参数与经纪商加收。

## Methodology and unit caveats
保证金比例、手续费按金额/手/单双边/平今等口径不同；不能用当前规则回填历史回测。

## Source-selection pitfalls
交易所静态合约规则页不一定覆盖临时风控通知；broker实际参数通常高于交易所最低标准。

## Provider cards
按交易所对应 provider；机构聚合见 `../../providers/wind-choice.md`。

## Copy-ready references
`../../references/futures-trading-parameters.md`。