# Dataset: US/HK/全球股票 K线

## What this dataset means
全球股票/ETF在明确交易所、时区、复权语义下的OHLCV时间序列。

## Common analytical uses
收益率、技术研究、事件窗口、跨资产比较和回测。

## Minimum canonical fields
`instrument_id, venue, timestamp/trade_date, timezone, open, high, low, close, adj_close, volume, currency, source_id`。

## Frequency and timing semantics
交易所时区与节假日必须保留；盘前/盘后与常规session不能无标记混合。

## Recommended sources
研究型US/HK历史K线可 shortlist `../../providers/yahoo.md`；机构生产和再分发考虑授权vendor。

## Alternatives / licensed alternatives
交易所/券商API、Bloomberg/LSEG/Wind/Choice等授权源。

## Methodology and unit caveats
close与adjusted close分开；拆股/分红调整语义要固定；跨币种收益比较需FX。

## Source-selection pitfalls
公开web endpoint的历史/分钟lookback和限流可能变化，不能当成有SLA的生产接口。

## Provider cards
`../../providers/yahoo.md`, `../../providers/wind-choice.md`。

## Copy-ready references
`../../references/global-equity-market-data.md`; verified reference `../../scripts/financial_data/adapters/yahoo_chart.py`。