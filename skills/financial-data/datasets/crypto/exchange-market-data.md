# Dataset: Crypto Exchange Market Data

## What this dataset means
加密交易所现货、永续/交割衍生品的ticker、K线、成交、盘口、OI、funding等市场数据。

## Common analytical uses
价格/成交、基差、资金费率、OI、跨所比较、微观结构和策略研究。

## Minimum canonical fields
`exchange, market_type, symbol, timestamp, price/OHLC, volume, quote_volume, bid/ask, open_interest, funding_rate, currency/unit, source_id`，按dataset裁剪。

## Frequency and timing semantics
24/7；必须使用UTC或明确时区。现货、USDT永续、币本位、交割合约分开。

## Recommended sources
优先交易所官方API；Binance见 `../../providers/binance.md`。其他交易所按项目所在地区与API条款单独增加。

## Alternatives / licensed alternatives
Coinbase/OKX等官方API、机构聚合商。

## Methodology and unit caveats
base volume与quote volume不同；contract size、funding interval、mark/index/last price分开；跨所symbol需标准化。

## Source-selection pitfalls
地区限制、接口权重、IP限流、产品下架和历史retention会变化；不要把一个交易所的市场代表整个Crypto市场。

## Provider cards
`../../providers/binance.md`。

## Copy-ready references
`../../references/fx-crypto.md`。