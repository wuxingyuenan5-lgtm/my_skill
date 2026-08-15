# Futures Positioning, Warehouse and Inventory

## Member position rankings

国内交易所常公布品种/合约成交、long OI、short OI 前 N 名会员。标准字段：trade_date、exchange、contract/product、rank、member、volume/change、long_oi/change、short_oi/change。

不要把“前20净多/净空”直接当全市场净持仓：只覆盖排名会员，且客户结构不可见。top20 concentration/net 等派生指标必须标 derived。

## CFTC COT

海外 positioning 见 `macro-positioning-events.md`。COT 分类是监管报表，不等于交易所 member ranking。

## Warehouse receipts / inventory

区分 registered warehouse receipt、exchange inventory、social/industry inventory、bonded inventory、deliverable stock。标准数据保存 `inventory_type`、location、unit、published_at、report_date、source。

## Delivery data

交割量、交割仓库、品牌/升贴水、注册/注销仓单适合产业研究，通常是低频 EOD/weekly 数据，不与实时交易 adapter 混在一起。
