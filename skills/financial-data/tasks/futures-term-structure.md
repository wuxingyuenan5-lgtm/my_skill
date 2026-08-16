# 国内期货主力 / 期限结构研究

## Objective
获取真实合约行情并研究主力选择、期限结构、Contango/Backwardation、跨期价差和连续合约。

## Required datasets
- `../datasets/futures/daily-contract-market-data.md`
- 合约主数据/乘数/到期：`../references/futures-contract-master.md`

## Optional datasets
- `../datasets/futures/member-position-ranking.md`：解释资金结构时才读。
- `../datasets/futures/warehouse-inventory.md`：研究库存驱动时才读。

## Recommended source path
优先使用对应交易所官方 exact-contract 数据；主力/连续/期限结构在项目本地按明确方法计算。

## Methodology / caveats
exact contract、dominant contract、continuous series 是不同对象；夜盘用交易所 trading day；settlement 与 close 分开；跨品种/跨所先统一乘数、币种、税费和单位。

## What to freeze into the downstream project
交易所 fetch recipe、合约主数据、主力选择规则、roll/adjustment 方法、交易日历、字段单位、last_verified。

## Avoid unnecessary reads
如果只做期限结构，不读取A股、SEC、全部 provider 或完整 capability index。