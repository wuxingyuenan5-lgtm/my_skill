# 碳酸锂（LC）研究数据路线

## Objective
为碳酸锂价格、期限结构、资金、仓单和产业供需研究建立最小数据清单。

## Required datasets
- `../datasets/futures/daily-contract-market-data.md`：GFEX LC全合约行情、结算、成交、OI。
- `../datasets/futures/member-position-ranking.md`：会员成交/多空持仓。

## Optional datasets
- `../datasets/futures/warehouse-inventory.md`
- `../datasets/futures/trading-parameters.md`
- 产业现货、库存、产量、开工率：当前详见 `../references/futures-commodities.md`，商业产业源通常需独立授权。

## Recommended source path
交易所层先读 `../providers/gfex.md`；产业现货/社会库存再按项目预算选择公开行业资料或 Wind/Choice/产业数据库。

## Methodology / caveats
区分交易所仓单与社会库存；夜盘交易日、交割月、合约乘数、结算价必须保留。产业数据往往是调查/估算，不与交易所官方事实混为一类。

## What to freeze into the downstream project
GFEX行情与持仓 recipe、LC合约规格、期限结构方法、仓单口径、产业数据定义/频率/授权、source timestamps。

## Avoid unnecessary reads
不要因为“研究碳酸锂”就加载所有商品、股票、宏观或全部交易所文档。