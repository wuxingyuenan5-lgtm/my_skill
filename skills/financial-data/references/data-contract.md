# Data Contract

`financial-data` 的核心不是“能抓到一个数字”，而是让同一个数字可复现、可审计、可比较。

## Standard observation

```yaml
instrument_id: equity_cn_600519_SH
symbol: 600519.SH
field: turnover
value: 6830000000
unit: CNY
currency: CNY
trade_date: 2026-08-14
calendar_date: null
report_period: null
publish_date: null
as_of: 2026-08-14T15:00:00+08:00
retrieved_at: 2026-08-15T11:00:00+08:00
source_id: tencent
source_type: secondary
adjustment: none
status: verified
quality_flags: []
metadata: {}
derived_from: []
algorithm_version: null
parameters: {}
```

## Required semantics

- `instrument_id`: internal canonical identity, not provider-specific secid.
- `symbol`: human-facing canonical ticker.
- `field`: normalized semantic field; provider field ID goes into metadata.
- `value` + `unit`: never return an unexplained naked number.
- `source_id`: exact provider family used.
- `as_of`: when the observation was valid according to the source.
- `retrieved_at`: when the system fetched it. Do not substitute retrieval time for provider time when provider time exists.

## Date dimensions

Keep these separate:

- `trade_date`: exchange trading session date.
- `calendar_date`: natural date for non-trading series when relevant.
- `report_period`: economic/accounting period the value describes.
- `publish_date`: official public-release date.
- `as_of`: point-in-time availability/validity.
- `retrieved_at`: retrieval timestamp.

A 2026Q2 revenue value filed in August is **not available in June backtests** merely because its `report_period` ends in June.

## Numeric conventions

- Percentage internal format: decimal (`3.21%` → `0.0321`).
- Currency values: explicit ISO-like currency unit (`CNY`, `USD`, `HKD`).
- Volume: explicit `shares`, `lots`, or `contracts`.
- Provider scale (`万`, `亿`, `M`, etc.) is normalized before cross-source comparison.
- Missing and zero are distinct. Missing fields stay absent/`None`; do not manufacture zero.

## Price adjustment

For historical price series set one of:

- `raw`
- `forward_adjusted`
- `backward_adjusted`
- `total_return_adjusted`

Never combine series with different adjustment conventions without an explicit conversion.

## Derived fields

Deterministic output records `derived_from`, `algorithm_version`, and parameters. Example: a 20-day SMA should identify its input price field and `period: 20`; a 10Y–2Y spread should identify both yield observations.
