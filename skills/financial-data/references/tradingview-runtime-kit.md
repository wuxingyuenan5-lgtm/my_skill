# TradingView / Chart Runtime Kit

Shipped reusable files:

```text
scripts/financial_data/charting.py
assets/tradingview/widget.html
assets/tradingview/lightweight-chart.html
assets/tradingview/datafeed-template.js
assets/tradingview/udf-fastapi-example.py
```

## Python transformations

```python
from financial_data.charting import (
    normalize_resolution,
    to_tradingview_bar,
    to_lightweight_bar,
    to_udf_history,
)
```

- Advanced Charts `Bar.time`: UTC Unix **milliseconds**.
- UDF `/history` `t`: Unix **seconds**.
- D/W/M Advanced Charts bars: use `trade_date` at 00:00 UTC; correct session placement through SymbolInfo/session/timezone, not manual visual offsets.
- UDF arrays are returned chronologically sorted.

## Own-data routes

**Advanced Charts:** copy `datafeed-template.js`, connect REST to historical backend and WebSocket to realtime bar builder. Each realtime callback sends the complete current bar.

**UDF:** copy `udf-fastapi-example.py`, replace demo storage with project DB/data module, implement symbol/session metadata and history query. This file does not include TradingView proprietary library code.

**Lightweight Charts:** copy `lightweight-chart.html` or its data adapter. Calculate proprietary indicators in your project and render additional series/panes.

**Widgets:** copy `widget.html` only when TradingView itself supports the public symbol and project does not need private/custom OHLCV.

See `tradingview.md` for full product choice, session/symbol mapping, futures specifics, marks and Pine-vs-custom-study distinctions.
