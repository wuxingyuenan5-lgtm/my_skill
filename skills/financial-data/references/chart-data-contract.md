# Chart Data Contract

Visualization should be separated from data acquisition.

A provider adapter produces canonical financial data. A chart adapter converts canonical data into TradingView Advanced Charts/UDF/Lightweight Charts or another visualization library.

## 1. Canonical OHLCV bar

```yaml
instrument_id: future_cn_shfe_cu_202609
symbol: CU2609.SHFE
timeframe: 5m
timestamp: 2026-08-15T09:30:00+08:00
trade_date: 2026-08-15
open: 78650
high: 78820
low: 78410
close: 78760
volume: 15234
volume_unit: contracts
open_interest: 287901
currency: CNY
price_unit: CNY/tonne
source_id: provider_x
adjustment: raw
```

The visualization layer should never have to infer `trade_date`, timezone, volume units or adjustment from an unlabeled dataframe.

## 2. Canonical scalar/time-series point

For indicators, breadth, basis, yield, inventory, etc.:

```yaml
instrument_id: future_cn_shfe_cu_202609
series_id: basis_pct
timestamp: 2026-08-15T15:00:00+08:00
value: 0.0125
unit: ratio
```

## 3. Canonical event/mark

For chart annotations:

```yaml
event_id: cu_roll_202609_202610
event_type: futures_roll
instrument_id: future_cn_shfe_cu_cont1
timestamp: 2026-08-20T15:00:00+08:00
title: Roll
text: CU continuous contract rolled from CU2609 to CU2610
source_id: local_roll_engine
```

Use this for earnings, filings, dividends, macro releases, futures roll dates, expiry and strategy signals.

## 4. Canonical order-book snapshot

```yaml
instrument_id: future_cn_cffex_if_202609
timestamp: 2026-08-15T10:01:02.100+08:00
bids:
  - [3821.2, 12]
  - [3821.0, 25]
asks:
  - [3821.4, 10]
  - [3821.6, 18]
price_unit: index_point
size_unit: contracts
```

DOM visualization is a separate transformation from candlestick bars.

## 5. Adapter outputs

Recommended converter boundaries:

```text
canonical bars
  -> tradingview_advanced_bar
  -> tradingview_udf_history
  -> lightweight_candles

canonical scalar series
  -> tradingview custom indicator source
  -> lightweight line/histogram series

canonical events
  -> tradingview marks/timescale marks
```

## 6. Why this contract exists

Do not bind a financial-data adapter to a front-end chart format.

Bad:

```text
exchange API -> TradingView UDF response
```

Preferred:

```text
exchange API -> canonical data -> validate/cache -> chart adapter -> TradingView UDF
```

This keeps source changes, methodology changes and visualization changes independent.

## 7. Continuous futures

A chart of a continuous futures series must carry derived-series metadata somewhere in the project even if the chart library only receives OHLCV:

```yaml
series_kind: continuous_future
selection_rule: max_open_interest
roll_rule: next_oi_gt_current_oi
adjustment: difference
methodology_version: cont_v1
```

The chart label should make it clear that the series is continuous/derived rather than an executable contract.

## 8. Time rules

Keep timezone-aware timestamps internally.

Only convert at the visualization boundary:

- Advanced Charts `Bar.time`: UTC milliseconds.
- UDF: protocol-specific Unix timestamps.
- Lightweight Charts: use the library-supported `Time` representation appropriate to the series.

For futures, preserve `trade_date` independently of the wall-clock timestamp.

## 9. Output profiles

A project may expose three chart payloads:

```text
compact: time + OHLC
standard: time + OHLCV
research: standard + OI + settlement + provenance/derived metadata
```

The front end can request the profile it needs without changing the source adapter.
