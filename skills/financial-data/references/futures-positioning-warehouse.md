# Futures Positioning, Warehouse and Inventory

## Member position rankings

国内交易所常公布品种/合约成交、long OI、short OI 前 N 名会员。**v0.2.3 已将可冻结的官方源接入 `futures-positioning-ready-core.md`**。

内部标准采用长表事实，而不是把三套排名按名次横向拼成同一会员：

```text
trade_date
exchange
scope_type
scope_id
variety
contract_id
ranking_type = volume | long | short
rank
member
value
change
source_id
source_url
raw
```

原因：成交第 1 名、持多第 1 名、持空第 1 名通常不是同一家会员。

当前 READY：SHFE / DCE / CZCE / CFFEX / GFEX。INE 官方日交易排名页面已确认，但当前机器 fetch path 尚未冻结，因此 umbrella `cn_futures_member_positions` 仍保持 RECIPE；详见 `futures-positioning-ready-core.md`。

不要把“前20净多/净空”直接当全市场净持仓：只覆盖排名披露会员，且客户结构不可见。Top5/10/20、long-minus-short、concentration 都是 derived。

集中度必须使用同合约、同交易日的市场总量作分母：成交排名用 total volume，多/空排名用 open interest；没有分母时不计算。

## CFTC COT

海外 positioning 见 `macro-positioning-events.md`。COT 分类是监管报表，不等于交易所 member ranking。

## Warehouse receipts / inventory

区分 registered warehouse receipt、exchange inventory、social/industry inventory、bonded inventory、deliverable stock。标准数据保存 `inventory_type`、location、unit、published_at、report_date、source。

仓单/库存仍是下一批 READY 化目标，不与 v0.2.3 member ranking runtime 混在一起。

## Delivery data

交割量、交割仓库、品牌/升贴水、注册/注销仓单适合产业研究，通常是低频 EOD/weekly 数据，不与实时交易 adapter 混在一起。
