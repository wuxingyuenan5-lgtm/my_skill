# Dataset: A股集合竞价

## What this dataset means
A-share call-auction snapshots or derived short-term auction-strength benchmarks for an explicit trading date/as-of stage. This is not ordinary continuous-session quote data.

## Common analytical uses
Opening-gap research, pre-open strength ranking, order-imbalance screening, event studies and intraday stock-pool construction.

## Minimum canonical fields
`instrument_id, trade_date, as_of, auction_stage, reference_price/auction_price, change_pct, volume, amount, imbalance_or_provider_fields, source_id, retrieved_at`.

Preserve provider-native fields that do not have a stable cross-provider equivalent instead of forcing false standardization.

## Frequency and timing semantics
Auction data is highly stage-sensitive. Record whether the result is realtime/in-progress or final, plus query time. Never mix pre-final snapshots with final auction values in one backtest without an explicit rule.

Historical research must only use data that was available at the historical decision time.

## Recommended sources
For structured Agent/API use, shortlist `../../providers/hithink-finance.md`, which currently exposes A-share auction snapshot and short-term benchmark capabilities.

Broker/Level-2 or exchange-licensed feeds may be required when exact order-level auction reconstruction or stronger production guarantees are needed.

## Methodology and unit caveats
- distinguish auction price/reference price from previous close and continuous-session open;
- declare amount/volume units;
- do not infer unexposed order-book depth from a vendor summary field;
- treat provider benchmark/ranking values as vendor-derived unless the methodology is fully replicated locally.

## Source-selection pitfalls
A source can return an expected empty/not-ready state before final auction data is published. Provider failure, rate limiting and legitimate no-data states must stay distinct.

## Provider cards
`../../providers/hithink-finance.md`.

## Copy-ready references
`../../references/source-recipes/hithink-finance.md`, `../../references/a-share-microstructure.md`.
