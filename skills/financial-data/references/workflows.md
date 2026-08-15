# Data Workflows

Workflows assemble reliable datasets; they do not produce buy/sell recommendations.

## Executable in v0.1.0

### `single_stock_snapshot(symbol)`
Chooses a small source-backed snapshot supported by the instrument/market. Unsupported components are explicit rather than fabricated.

### `peer_comparison(symbols, fields)`
Runs the same normalized fields across peers and merges provenance/errors. Useful as input to an analyst's comparison, not as an investment ranking engine.

### `macro_snapshot()`
Fetches the US Treasury curve through the official adapter.

### `event_dataset(symbol, form=None)`
Fetches SEC filing metadata for US issuers; optional form filter (e.g. `10-Q`, `8-K`).

### `market_breadth_snapshot(changes)`
Pure local calculation from an already-supplied return/change vector.

## Defined but intentionally unsupported in v0.1.0

- `sector_rotation_dataset`: requires market-wide classification/performance adapters.
- `cross_section_fundamentals`: requires SEC Frames / equivalent market-wide adapter.

They return `FIELD_NOT_SUPPORTED` with the missing capability rather than fake rows.

## Point-in-time discipline

For historical studies, workflows must use data available at the historical decision timestamp. Financial report period alone is insufficient; preserve filed/published dates and avoid look-ahead.
