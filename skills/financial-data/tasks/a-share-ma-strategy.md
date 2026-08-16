# A股均线 / 技术策略研究

## Objective
为A股均线、趋势、动量和技术策略研究确定最小数据集，不把研究任务扩展成全市场数据工程。

## Required datasets
- `../datasets/cn-equity/kline.md`：复权/不复权 OHLCV、成交额。
- 交易日历与证券身份：见 `../references/trading-calendar.md`、`../references/instrument-master.md`。

## Optional datasets
- `../datasets/cn-equity/market-cross-section.md`：做股票池、流动性/成交额过滤时再读。
- `../datasets/cn-equity/industry-classification.md`：做行业中性或行业分组时再读。

## Recommended source path
先读 K线 dataset 卡；A股研究型历史K线通常先 shortlist Tencent，必要时再比较 Sina/Eastmoney 或 Wind/Choice。

## Methodology / caveats
统一复权方式；避免用复权价格反推真实成交额；处理停牌、上市初期、退市与幸存者偏差。回测若使用动态股票池，行业/成分必须 point-in-time。

## What to freeze into the downstream project
标的身份映射、K线 recipe、复权口径、交易日历、缺失K线规则、数据源与 fallback、last_verified。

## Avoid unnecessary reads
无需读取期货、SEC、宏观、Crypto、全部 provider 卡或完整 capability index。