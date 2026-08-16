# Dataset: 期货仓单 / 库存

## What this dataset means
交易所注册/有效仓单、指定交割仓库库存或周度库存等官方交割体系数据；不等同于社会库存、港口库存、工厂库存或全产业物理库存。

## Common analytical uses
交割压力、库存周期、基差、期限结构、供需紧张度和库存变化验证。

## Minimum canonical fields
`trade_date, exchange, variety/contract, warehouse/region, receipt_qty, change, unit, receipt_status, source_id, source_url`；社会库存另建字段体系。

## Frequency and timing semantics
交易所仓单多为日频，库存统计可能日/周频；必须保存数据对应日期与发布时间。

## Recommended sources
对应交易所官方；产业社会库存另选行业协会/调研机构/授权数据库，不混用定义。

## Alternatives / licensed alternatives
Wind/Choice、产业数据库、协会/公司披露。

## Methodology and unit caveats
注册仓单、有效仓单、注销仓单、库存、可交割库存概念分开；跨品种单位需标准化。

## Source-selection pitfalls
不同交易所报表颗粒度、仓库/地区字段和历史格式不同；当前本Skill主要提供 recipe 指引而非统一runtime。

## Provider cards
按交易所读 `../../providers/shfe.md`、`../../providers/ine.md`、`../../providers/dce.md`、`../../providers/czce.md`、`../../providers/gfex.md` 等。

## Copy-ready references
`../../references/futures-positioning-warehouse.md`。