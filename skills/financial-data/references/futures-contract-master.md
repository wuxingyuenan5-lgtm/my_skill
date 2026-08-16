# Futures Contract Master

期货项目必须先有 Contract Master，再谈 K线/主力/连续。产品代码不是可交易合约。

## Canonical identity

```yaml
canonical_id: future_cn_shfe_cu_202609
asset_class: future
exchange: SHFE
product: CU
contract_id: CU2609
delivery_month: 2026-09
currency: CNY
price_unit: CNY/tonne
multiplier: 5
multiplier_unit: tonne/contract
tick_size: 10
listed_date:
last_trade_date:
delivery_start:
delivery_end:
has_night_session: true
session_profile: shfe_cu
source_definition: exchange_official
```

Product master 保存长期规则；Contract master 保存每月具体合约生命周期与当期参数。

同一合约可能有 exchange symbol、vendor symbol、broker/CTP InstrumentID、TradingView alias 和 internal canonical ID。内部 ID 不应直接等于任何单一供应商 symbol。

## Main/dominant contract

“主力”不是法定合约类型。必须保存方法，例如最大 OI、最大成交量、vendor-defined main 或复合规则，并记录 selection time、roll hysteresis。不要无说明使用“主连”。
