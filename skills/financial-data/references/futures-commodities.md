# Futures, Commodities and Derivatives Data Handbook

This module treats futures as a first-class asset class, not as a special case of equity market data.

The goal is to let a downstream project select the exact futures data it needs once, copy the chosen source/recipe into the project, and then operate independently of this Skill.

## 1. Futures data model

Every futures observation should identify at least:

- `exchange`
- `product` / root symbol
- `contract_id` (exact delivery month/year)
- `trade_date`
- wall-clock timestamp and timezone for intraday data
- quote currency
- price unit (CNY/tonne, USD/oz, index points, etc.)
- contract multiplier
- tick size
- volume unit (`contracts` / lots)
- open-interest convention
- source and retrieval time

Do not use a product root such as `CU`, `IF`, `GC` as though it were a tradable contract. `CU`, `IF`, `GC` describe products; `CU2609`, `IF2609`, `GCZ26` describe contracts.

## 2. Contract master

A project that uses futures for more than a one-off query should persist a contract master.

Recommended fields:

```yaml
canonical_id: future_cn_shfe_cu_202609
exchange: SHFE
product: CU
contract_id: CU2609
name: 沪铜2609
asset_class: future
currency: CNY
price_unit: CNY/tonne
multiplier: 5
multiplier_unit: tonne/contract
tick_size: 10
listed_date: null
last_trade_date: null
delivery_month: 2026-09
has_night_session: true
source_definition: exchange
```

Maintain exchange product rules separately from individual contract lifecycle metadata.

## 3. China futures exchanges

The handbook should cover all major mainland exchanges as separate source families:

- SHFE — Shanghai Futures Exchange
- INE — Shanghai International Energy Exchange
- DCE — Dalian Commodity Exchange
- CZCE — Zhengzhou Commodity Exchange
- CFFEX — China Financial Futures Exchange
- GFEX — Guangzhou Futures Exchange

### Official-source priority

For settlement, contract parameters, delivery rules, warehouse receipts, position rankings, margin/limit changes and exchange calendars, prefer the exchange itself over portals.

For high-frequency/intraday quote retrieval, a licensed terminal/vendor or a trading gateway may be more practical; retain the exchange source as the definition/verification source.

### Official data categories worth keeping

The Skill should maintain recipes for, where the exchange publishes them:

- delayed quotes
- daily OHLC / settlement
- weekly/monthly statistics
- historical data downloads
- trading calendar and sessions
- contract specifications
- settlement parameters
- margin requirements
- price-limit parameters
- fees
- delivery rules
- warehouse receipt daily reports
- inventory weekly reports
- delivery warehouse / brand information
- member volume and long/short open-interest rankings
- delivery statistics
- option daily statistics and Greeks where published

Example official exchange pages:

- SHFE data/report center: https://www.shfe.com.cn/reports/tradedata/dailyandweeklydata/
- CFFEX daily statistics: https://www.cffex.com.cn/rtj/
- CFFEX position ranking: https://www.cffex.com.cn/ccpm/
- GFEX historical/market data entry: https://www.gfex.com.cn/

Exchange webpage endpoints are implementation details and can change. A project recipe should therefore record `last_verified`, expected content type and a parser fixture.

## 4. China futures practical source layers

Recommended routing model:

### Definition / settlement / delivery layer

Priority:

1. exchange official publication
2. licensed vendor (Wind / Choice / Bloomberg / Refinitiv if available)
3. reputable public-data adapter

### Intraday / streaming layer

Possible project routes:

1. broker/CTP market-data gateway for domestic futures
2. licensed market-data vendor
3. public web quote source for research-only use

Do not treat an exchange daily settlement table as a substitute for a real-time feed.

### Research convenience layer

For non-production research, maintain recipes for common Python ecosystems (for example AkShare-like wrappers) only as convenience adapters. The recipe must still identify the underlying source and should not make the wrapper the provenance source.

## 5. Global futures

Maintain a separate source matrix for:

- CME / CBOT / NYMEX / COMEX
- ICE
- LME
- Eurex
- SGX
- HKEX derivatives where terms permit

Key products include:

- equity index futures: ES/NQ/RTY, etc.
- rates: Treasury futures, SOFR futures
- energy: WTI/Brent/natural gas
- metals: gold/silver/copper
- agriculture
- FX futures

For global real-time data, licensing and redistribution restrictions are material. Treat exchange contract definitions as official reference data and obtain live market data through an authorized route appropriate to the project.

## 6. Trading date and night-session semantics

A futures `trade_date` is not always the same as the wall-clock calendar date.

For Chinese night sessions, an evening timestamp can belong to the following exchange trading day. Preserve both:

```yaml
calendar_timestamp: 2026-08-14T21:30:00+08:00
trade_date: 2026-08-15
```

Never group futures bars into daily returns solely with `timestamp.date()`.

Maintain an exchange-specific trading-calendar/session table.

## 7. OHLC, settlement and reference prices

These fields are distinct:

- `last`
- `close`
- `settlement`
- `previous_settlement`
- `open`
- `high`
- `low`
- `vwap`

Do not substitute `close` for `settlement` in margin/PnL logic unless the methodology explicitly does so.

For CFFEX, for example, the exchange's daily statistics distinguish close, settlement and previous settlement and document turnover/open-interest units.

## 8. Main, secondary and dominant contracts

`main_contract` is a derived selection, not an exchange security.

Recommended standard fields:

```yaml
selection_rule: max_open_interest
selection_time: close
minimum_days_to_expiry: 0
tie_breaker: volume
switch_buffer: 0.00
```

Useful rules:

- maximum open interest
- maximum volume
- vendor-defined dominant contract
- liquidity score = weighted OI + volume

A downstream project must persist the rule/version if it expects reproducible history.

## 9. Continuous futures

A continuous series is derived and must be labeled accordingly.

Required metadata:

```yaml
continuous:
  selection_rule: max_open_interest
  roll_trigger: next_contract_oi > current_contract_oi
  roll_time: close
  adjustment: difference
  roll_calendar_version: v1
```

Common adjustment modes:

- raw splice: preserves traded prices but creates roll gaps
- difference adjusted: additive back-adjustment
- ratio adjusted: multiplicative back-adjustment
- total-return style: model the PnL of rolling actual contracts

Never use a back-adjusted price level as though it were an executable historical contract price.

## 10. Term structure / curve

A curve snapshot should contain all liquid contracts for one product at a common observation time.

Recommended schema:

```text
contract_id
expiry / delivery_month
last
settlement
volume
open_interest
days_to_expiry
annualized_carry (optional)
```

Derived outputs:

- nearby spread
- calendar spread matrix
- contango/backwardation
- annualized roll yield
- curve slope/curvature
- main-to-next spread

Never compare contracts sampled at materially different times without flagging the mismatch.

## 11. Basis and cross-market spreads

For futures basis:

```text
basis = futures_price - spot_reference
basis_pct = futures_price / spot_reference - 1
annualized_basis = basis_pct * annualization_factor
```

The exact spot/reference definition must be stored.

For cross-exchange commodities (SHFE/LME/COMEX etc.), normalize:

- currency
- weight/volume unit
- contract size
- tax/VAT treatment
- delivery location/grade
- trading time
- FX timestamp

Do not label a raw price difference as an arbitrage spread before these transformations.

## 12. Open interest and member positioning

Store open interest separately from volume.

For exchange member rankings, distinguish:

- member volume
- long open interest
- short open interest
- day-over-day change
- whether values are single-side or double-side counted
- ranking coverage threshold

Useful derived metrics:

- top-N long concentration
- top-N short concentration
- net top-member exposure
- concentration change

Do not infer end-client positions from member-level data without qualification.

## 13. Warehouse receipts, inventory and delivery

For physical commodities, the Skill should cover:

- registered warehouse receipts
- receipt additions/cancellations where available
- weekly inventory
- delivery volumes
- warehouse/location breakdown
- deliverable brands/grades
- premiums/discounts

Recommended semantic distinction:

```text
warehouse_receipt != social_inventory != exchange_inventory != bonded_inventory
```

Each field needs its own definition_source/methodology_id.

## 14. Margin, price limits and fees

These are time-varying parameters.

Never hard-code a single leverage number for a futures product.

Store:

```yaml
effective_from:
effective_to:
exchange_margin_rate:
broker_margin_rate: null
price_limit_pct:
open_fee:
close_fee:
close_today_fee:
fee_unit:
source:
```

Separate exchange minimum margin from the broker's actual customer margin.

## 15. Futures options

Common fields:

- underlying futures contract
- expiry
- strike
- call/put
- last/bid/ask
- volume
- open interest
- settlement
- IV
- delta/gamma/theta/vega where supplied or locally derived

If Greeks are locally computed, record pricing model, rate, dividend/carry assumption, underlying reference and algorithm version.

## 16. Project-export recipes

When a project asks for futures data, the Skill should be able to emit a self-contained module such as:

```text
data/futures/
  contract_master.py
  calendar.py
  market_data.py
  settlement.py
  positions.py
  warehouse.py
  continuous.py
  curve.py
  sources.md
```

Only include the modules the project needs.

## 17. Source health / parser health

For every futures source recipe keep:

```yaml
status: healthy | degraded | broken | deprecated | restricted
last_verified:
content_type:
rate_limit:
auth:
known_issues:
fallback:
```

Exchange website redesigns are common enough that parser health should be separated from data-source authority.

## 18. High-value standard workflows

The manual should support these repeatable tasks:

- exact contract quote/history
- dominant-contract selection
- continuous series construction
- futures curve snapshot
- basis/annualized basis
- member positioning concentration
- warehouse/inventory monitor
- margin/limit/fee lookup
- contract specification lookup
- expiry/roll calendar
- futures-option chain/IV
- cross-market commodity spread normalization

These workflows prepare data and methodology; they do not make trade recommendations.
