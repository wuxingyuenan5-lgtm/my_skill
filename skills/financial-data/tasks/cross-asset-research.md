# 跨资产研究 / 交易晨报数据路线

## Objective
按研究问题选择全球股票、利率、商品、FX、Crypto和中国市场数据，而不是预先加载全百科。

## Required datasets
按当次报告模块选择：美股/港股 `../datasets/global-equity/kline.md`；美国利率 `../datasets/macro/us-rates-treasury.md`；中国期货 `../datasets/futures/daily-contract-market-data.md`；Crypto `../datasets/crypto/exchange-market-data.md`；A股横截面 `../datasets/cn-equity/market-cross-section.md`。

## Optional datasets
CFTC `../datasets/macro/cftc-positioning.md`、期货席位、仓单、SEC、产业数据仅在当次研究需要时增加。

## Recommended source path
先按模块 shortlist dataset，再进入每个 dataset 推荐的1个主源和必要备源；官方宏观/交易所事实优先，vendor派生数据独立标识。

## Methodology / caveats
统一 as_of、retrieved_at、timezone、currency、unit；宏观发布时间与市场收盘时间不可混用；同一报告冻结一次数据截面。

## What to freeze into the downstream project
报告自己的 source map、字段合同、时点规则、fallback、质量校验和可用性监控；日常生产不继续依赖 Skill。

## Avoid unnecessary reads
不要把“跨资产”解释成每次必须读所有 asset/provider 文档；以报告栏目和当日研究问题裁剪。