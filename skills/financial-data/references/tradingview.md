# TradingView Integration Handbook

TradingView is not one single API. Treat the following products as separate integration paths.

## 1. Product map

### A. TradingView Widgets

Use when the project wants the fastest possible embedded chart/watchlist/market overview using TradingView-provided market data.

Characteristics:

- copy/paste HTML or React/Web Component integration
- TradingView supplies the widget data
- good for supported public symbols
- no custom project datafeed
- low implementation cost

Typical use cases:

- single-symbol advanced chart
- mini chart
- ticker tape
- market overview
- market quotes/watchlist
- economic/calendar widgets where available

Do not present Widgets as a way to upload arbitrary private OHLCV data.

Official docs:
https://www.tradingview.com/widget-docs/

### B. Advanced Charts / Charting Library

Use when the project wants a TradingView-class chart UI but supplies its own market data.

Important facts:

- the library itself contains no market data
- the project implements a Datafeed API or UDF backend
- historical data can come from REST/database/files via a backend bridge
- real-time updates can be streamed through WebSocket and delivered via `subscribeBars`
- supports TradingView's rich chart UI and built-in technical studies
- custom indicators are implemented in JavaScript; Pine Script is not supported inside Advanced Charts/Trading Platform
- access is distributed through TradingView's private repository and the library is not redistributable

Official docs:
https://www.tradingview.com/charting-library-docs/latest/

### C. Lightweight Charts

Use when the project owns its data and wants a lightweight, open-source TradingView-style chart component without the full TradingView terminal UI.

Characteristics:

- open source / Apache-2.0
- data is supplied directly by the project
- excellent for dashboards, custom research pages and reusable internal chart components
- supports real-time updates
- much lighter than Advanced Charts
- no built-in indicator library comparable to Advanced Charts; calculate indicators in the project and add them as additional series/panes

Official site:
https://www.tradingview.com/lightweight-charts/

### D. Trading Platform / Broker API

Use only when the project is integrating trading/broker functionality into the TradingView-style terminal.

In addition to Datafeed API, Trading Platform requires Broker API and quote-related methods for order ticket, watchlist, DOM and trading workflows.

This is different from a market-data-only project.

## 2. Recommended routing decision

```text
Need TradingView's own symbols/data and fastest embed?
  -> Widget

Need full TradingView chart UX + your own data?
  -> Advanced Charts + Datafeed API

Need your own data + lightweight/open-source visualization?
  -> Lightweight Charts

Need chart-based order execution / broker terminal?
  -> Trading Platform + Datafeed + Broker API
```

For most internally developed research/monitoring platforms, default to:

1. Lightweight Charts for open-source custom dashboards.
2. Advanced Charts if the richer TradingView chart UI is strategically important and license/access conditions fit the deployment.
3. Widgets for public supported symbols where zero custom data processing is needed.

## 3. TradingView symbol mapping

Maintain a project-level mapping instead of assuming the project's canonical symbol equals TradingView's symbol.

Example:

```yaml
canonical_id: future_us_cme_es_continuous_1
canonical_ticker: ES.CONT1
tradingview:
  symbol: CME_MINI:ES1!
  product_type: futures
```

```yaml
canonical_id: equity_us_aapl
canonical_ticker: AAPL.US
tradingview:
  symbol: NASDAQ:AAPL
  product_type: stock
```

The TradingView symbol string is a presentation/integration alias, not the internal master ID.

For Widgets, verify the exact TradingView symbol in TradingView's symbol search before freezing it into a production project.

## 4. Datafeed API mental model

Advanced Charts calls your JavaScript datafeed. Your datafeed calls your backend.

```text
Advanced Charts
   ↓ onReady / searchSymbols / resolveSymbol / getBars / subscribeBars
JavaScript Datafeed
   ↓ REST / WebSocket
Project Backend
   ↓
Database / exchange API / vendor / financial-data recipe
```

TradingView does not fetch your database directly.

## 5. Required Datafeed methods

A minimal custom Datafeed API implementation should cover:

- `onReady`
- `searchSymbols`
- `resolveSymbol`
- `getBars`
- `subscribeBars`
- `unsubscribeBars`

Additional methods can provide marks, server time, quotes and Trading Platform functionality.

Keep Datafeed callbacks asynchronous.

## 6. SymbolInfo format

For every project symbol map the project's instrument metadata into TradingView's `LibrarySymbolInfo`.

Important fields include:

```javascript
{
  name: "CU2609",
  ticker: "SHFE:CU2609",
  description: "Copper Sep 2026",
  type: "futures",
  exchange: "SHFE",
  listed_exchange: "SHFE",
  timezone: "Asia/Shanghai",
  session: "0900-1015,1030-1130,1330-1500,2100-0100",
  minmov: 1,
  pricescale: 1,
  has_intraday: true,
  has_daily: true,
  supported_resolutions: ["1", "5", "15", "30", "60", "240", "1D"]
}
```

The session above is only an illustration. Futures sessions vary by product and can change; generate them from an exchange/product session table rather than hard-coding one string for all Chinese futures.

`timezone` must use a TradingView-supported/Olson timezone identifier.

`pricescale` represents the display precision. For a decimal price with `n` decimal places, use `10^n` unless a fractional price convention applies.

## 7. Advanced Charts Bar format

Historical/realtime OHLCV bars use:

```javascript
{
  time: 1786709400000,
  open: 78650,
  high: 78820,
  low: 78410,
  close: 78760,
  volume: 15234
}
```

`time` is milliseconds since Unix epoch in UTC for the `Bar` interface.

For daily/weekly/monthly bars, TradingView expects the timestamp for the trading day at 00:00 UTC rather than the beginning of the exchange session. For intraday bars, use the actual bar-start UTC timestamp aligned to the declared exchange session.

Do not manually shift bar timestamps to make the visual chart "look right". Correct the symbol session/timezone metadata instead.

## 8. Universal internal -> TradingView bar conversion

Recommended internal bar schema:

```python
{
    "timestamp": "2026-08-15T09:30:00+08:00",
    "trade_date": "2026-08-15",
    "open": 100.0,
    "high": 102.0,
    "low": 99.5,
    "close": 101.5,
    "volume": 12345,
}
```

Advanced Charts conversion:

```python
from datetime import datetime, timezone


def to_tv_bar(row: dict) -> dict:
    dt = datetime.fromisoformat(row["timestamp"])
    if dt.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return {
        "time": int(dt.astimezone(timezone.utc).timestamp() * 1000),
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "close": float(row["close"]),
        "volume": float(row["volume"]) if row.get("volume") is not None else None,
    }
```

For D/W/M bars, build `time` from `trade_date` at `00:00:00 UTC` rather than using a market-session timestamp.

## 9. UDF backend

UDF is the simplest HTTP bridge for Advanced Charts.

Useful endpoints:

```text
GET /config
GET /search?query=&type=&exchange=&limit=
GET /symbols?symbol=
GET /history?symbol=&from=&to=&resolution=&countback=
GET /time
GET /marks
```

The backend can be implemented in Python, Node, Go, etc.

Basic Flask-like history example:

```python
@app.get("/history")
def history():
    symbol = request.args["symbol"]
    resolution = request.args["resolution"]
    from_ts = int(request.args["from"])
    to_ts = int(request.args["to"])

    bars = load_project_bars(symbol, resolution, from_ts, to_ts)
    if not bars:
        return {"s": "no_data"}

    return {
        "s": "ok",
        "t": [int(b["time"] / 1000) for b in bars],
        "o": [b["open"] for b in bars],
        "h": [b["high"] for b in bars],
        "l": [b["low"] for b in bars],
        "c": [b["close"] for b in bars],
        "v": [b.get("volume", 0) for b in bars],
    }
```

Note the UDF HTTP history format uses timestamp arrays appropriate to the UDF protocol; keep protocol conversion isolated from the internal canonical data model.

## 10. Real-time Datafeed

Recommended architecture:

```text
provider websocket / CTP / internal stream
        ↓
backend bar builder
        ↓ websocket
frontend datafeed
        ↓ onTick(complete_current_bar)
Advanced Charts
```

`subscribeBars` should send the complete current OHLCV bar for each update, not only a delta/tick.

Maintain independent subscriptions by symbol + resolution + currency/chart context.

## 11. Resolution mapping

TradingView resolution strings commonly include:

```text
1       1 minute
5       5 minutes
15      15 minutes
60      1 hour
240     4 hours
1D / D  1 day
1W / W  1 week
1M / M  1 month
```

Do not confuse `1M` (one month) with one minute (`1`).

Keep a project mapping:

```python
TV_TO_INTERNAL = {
    "1": "1m",
    "5": "5m",
    "15": "15m",
    "30": "30m",
    "60": "1h",
    "240": "4h",
    "1D": "1d",
    "D": "1d",
    "1W": "1w",
    "W": "1w",
    "1M": "1mo",
    "M": "1mo",
}
```

## 12. Futures-specific TradingView integration

Futures need extra care:

- map exact contracts separately from continuous contracts
- use product-specific trading sessions
- preserve exchange trading date for night sessions
- expose expiry where supported
- do not chart a back-adjusted continuous series under a real contract symbol
- show settlement separately if the project's analysis uses settlement rather than close

Recommended custom symbols:

```text
MYDATA:CU2609
MYDATA:CU_CONT1
MYDATA:IF2609
MYDATA:IF_CONT1
```

The user-facing chart symbol can differ from the backend `ticker` as long as the mapping is deterministic.

## 13. Marks / events on charts

Advanced Charts UDF/Datafeed supports marks/timescale marks.

Useful financial marks:

- earnings
- dividends
- filings
- futures roll dates
- expiry
- margin/limit changes
- macro releases
- corporate actions
- strategy signals

This is a strong integration point between the financial-data handbook and visual research tools.

## 14. Custom indicators

Advanced Charts supports many built-in studies and JavaScript custom indicators.

Pine Script cannot be loaded directly into Advanced Charts/Trading Platform.

Therefore keep two separate recipes:

```text
TradingView.com Pine Script
  -> scripts intended to run on tradingview.com

Advanced Charts custom study
  -> JavaScript custom indicator for your own embedded chart
```

Do not tell a project to copy Pine code into Advanced Charts.

## 15. Lightweight Charts with own data

Lightweight Charts is often the simplest solution for internal custom data.

Frontend pattern:

```javascript
import { createChart, CandlestickSeries, HistogramSeries } from 'lightweight-charts';

const chart = createChart(container, { autoSize: true });
const candles = chart.addSeries(CandlestickSeries);

candles.setData([
  { time: '2026-08-13', open: 100, high: 103, low: 99, close: 102 },
  { time: '2026-08-14', open: 102, high: 104, low: 101, close: 103 },
]);
```

For project-defined indicators, calculate them in Python/JavaScript and add another line/histogram series or pane.

Recommended use cases:

- A-share monitoring dashboard
- futures curve/contract chart
- backtest visualization
- strategy equity curve
- custom breadth indicator
- proprietary internal data

## 16. Widget recipe generator

For public/supported TradingView symbols, keep copy-ready widget recipes.

Example Advanced Real-Time Chart style embed pattern:

```html
<div class="tradingview-widget-container">
  <div id="tradingview_chart"></div>
  <script src="https://s3.tradingview.com/tv.js"></script>
  <script>
    new TradingView.widget({
      container_id: "tradingview_chart",
      symbol: "NASDAQ:AAPL",
      interval: "D",
      autosize: true,
      theme: "dark",
      locale: "zh_CN"
    });
  </script>
</div>
```

TradingView is moving many Widgets toward current Web Component formats. When exporting a project recipe, prefer the current code generated by TradingView's official Widget configurator rather than assuming an old embed snippet remains canonical.

## 17. What TradingView is NOT in this Skill

Do not treat TradingView as a generic unofficial data-scraping API.

The handbook should distinguish:

- `TradingView Widget`: display TradingView-provided data
- `TradingView Advanced Charts`: display your data
- `TradingView Lightweight Charts`: render your data with open-source chart components
- `TradingView website/Pine`: indicator environment on tradingview.com
- `Trading Platform/Broker API`: trading integration

If a project wants raw market data, route it to the appropriate exchange/vendor/source recipe first; use TradingView as the visualization/integration layer unless an official TradingView product explicitly supplies the data (such as Widgets).

## 18. Project export templates

The Skill should be able to emit one of these packs.

### Widget-only

```text
visualization/tradingview/
  widgets.html
  symbols.json
  README.md
```

### Advanced Charts + own data

```text
visualization/tradingview/
  datafeed.js
  symbol_mapper.js
  resolution_mapper.js
  websocket.js
backend/
  udf.py or datafeed endpoints
  bar_service.py
  symbol_service.py
  event_marks.py
README.md
```

Do not include TradingView's non-redistributable Advanced Charts library files in a public generated repository. The project owner must obtain them through TradingView's official access process.

### Lightweight Charts

```text
visualization/lightweight-charts/
  chart.js
  series.js
  data_adapter.js
  README.md
```

## 19. Version and compatibility notes

TradingView chart libraries evolve. Recipes should record:

```yaml
tradingview_product: advanced_charts
library_version: 32.x
last_verified:
api_mode: datafeed
```

When updating Advanced Charts, review TradingView's release notes for breaking API changes.

## 20. Recommended Skill capability labels

Use:

```text
TV_WIDGET_READY
TV_ADVANCED_CHARTS_RECIPE
TV_UDF_RECIPE
TV_DATAFEED_RECIPE
TV_LIGHTWEIGHT_READY
TV_BROKER_RESTRICTED
```

This makes it obvious whether a recipe supplies TradingView data, displays project data, or requires additional licensing/access.
