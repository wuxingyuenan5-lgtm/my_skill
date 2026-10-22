# Dataset: A股特色行情 / 市场微观结构与热度

## What this dataset means
Vendor-structured A-share event/state datasets such as limit-up, limit-down, limit-break, consecutive-limit ladders, anomaly reasons, hot-stock rankings and dragon-tiger lists.

These datasets are not interchangeable with raw exchange quotes. Many fields are vendor-derived or editorially classified.

## Common analytical uses
Market-breadth and sentiment monitoring, limit-state studies, event-driven stock pools, popularity/attention factors, anomaly detection, short-horizon cross-sectional research and post-close review.

## Minimum canonical fields
For event-list datasets preserve at minimum:

`instrument_id, trade_date, event_type, event_time/as_of, rank_or_state, provider_reason_or_tag, source_id, retrieved_at`.

Add event-specific fields such as limit price, seal amount, break count, consecutive-board count, turnover, institution/active-seat metadata or ranking values only when their semantics are documented.

## Frequency and timing semantics
Some capabilities are current-day or date-bounded. Always persist the requested trade date and retrieval time. Historical hot-list/constituent data must not be backfilled from today's snapshot.

## Recommended sources
- Structured API/Agent path: `../../providers/hithink-finance.md`.
- Public-web research/fallback for selected pools and cross-checks: `../../providers/eastmoney.md`.
- THS public-web/editorial labels remain a separate provider family where the Financial-API contract does not expose an equivalent field.
- Exchange/CNINFO sources should be used for authoritative regulatory definitions or original disclosures where applicable.

## Methodology and classification caveats
- `limit_up`, `limit_down`, `limit_break`, `hot_rank`, `anomaly_reason` and `dragon_tiger` are separate event classes; do not collapse them into one generic sentiment flag.
- Vendor reason/theme/anomaly labels must be tagged `vendor_derived` or `vendor_editorial`.
- Rank changes are ordinal unless the provider documents a cardinal score.
- Dragon-tiger lists are disclosed subsets, not full-market flow or complete investor positioning.

## Source-selection pitfalls
A provider can legitimately return empty data on a non-trading date or before a dataset is ready. Distinguish this from auth failure, throttling and server errors.

## Provider cards
`../../providers/hithink-finance.md`, `../../providers/eastmoney.md`.

## Copy-ready references
`../../references/a-share-microstructure.md`, `../../references/a-share-flows-positioning.md`, `../../references/source-recipes/hithink-finance.md`.
