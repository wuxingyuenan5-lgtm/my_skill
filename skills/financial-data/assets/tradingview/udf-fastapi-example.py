"""Minimal TradingView UDF backend example for project-owned data.

Copy this file into a downstream project and replace DEMO_SYMBOL/BARS with the
project's own repository/database queries. TradingView Advanced Charts library
files are not included here.
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="TradingView UDF example")

DEMO_SYMBOL = {
    "name": "600519.SH",
    "ticker": "600519.SH",
    "description": "Project custom data",
    "type": "stock",
    "session": "0930-1130,1300-1500",
    "timezone": "Asia/Shanghai",
    "exchange": "PROJECT",
    "listed_exchange": "PROJECT",
    "minmov": 1,
    "pricescale": 100,
    "has_intraday": True,
    "has_daily": True,
    "supported_resolutions": ["1", "5", "15", "30", "60", "240", "1D", "1W", "1M"],
    "volume_precision": 0,
    "data_status": "streaming",
}

# UDF `/history` uses Unix seconds, unlike Advanced Charts Bar.time in the
# JavaScript Datafeed API where time is milliseconds.
BARS = [
    {"time": 1786709400, "open": 100.0, "high": 101.0, "low": 99.5, "close": 100.5, "volume": 1000.0},
    {"time": 1786709460, "open": 100.5, "high": 101.5, "low": 100.2, "close": 101.2, "volume": 1200.0},
]


@app.get("/config")
def config() -> dict[str, Any]:
    return {
        "supported_resolutions": DEMO_SYMBOL["supported_resolutions"],
        "supports_group_request": False,
        "supports_marks": False,
        "supports_search": True,
        "supports_timescale_marks": False,
    }


@app.get("/search")
def search(query: str = "", exchange: str = "", type: str = "", limit: int = 30):
    query_lower = query.lower().strip()
    if query_lower and query_lower not in DEMO_SYMBOL["name"].lower() and query_lower not in DEMO_SYMBOL["description"].lower():
        return []
    return [{
        "symbol": DEMO_SYMBOL["name"],
        "full_name": DEMO_SYMBOL["name"],
        "description": DEMO_SYMBOL["description"],
        "exchange": DEMO_SYMBOL["exchange"],
        "ticker": DEMO_SYMBOL["ticker"],
        "type": DEMO_SYMBOL["type"],
    }][:limit]


@app.get("/symbols")
def symbols(symbol: str = Query(...)):
    if symbol not in {DEMO_SYMBOL["name"], DEMO_SYMBOL["ticker"]}:
        raise HTTPException(status_code=404, detail="unknown_symbol")
    return DEMO_SYMBOL


@app.get("/history")
def history(symbol: str, resolution: str, from_: int = Query(alias="from"), to: int = Query(...), countback: int = 0):
    if symbol not in {DEMO_SYMBOL["name"], DEMO_SYMBOL["ticker"]}:
        return {"s": "error", "errmsg": "unknown_symbol"}
    rows = [row for row in BARS if from_ <= row["time"] <= to]
    if countback > 0 and len(rows) < countback:
        prior = [row for row in BARS if row["time"] < from_]
        rows = prior[-(countback - len(rows)):] + rows
    rows.sort(key=lambda row: row["time"])
    if not rows:
        return {"s": "no_data"}
    return {
        "s": "ok",
        "t": [r["time"] for r in rows],
        "o": [r["open"] for r in rows],
        "h": [r["high"] for r in rows],
        "l": [r["low"] for r in rows],
        "c": [r["close"] for r in rows],
        "v": [r["volume"] for r in rows],
    }


@app.get("/time")
def server_time() -> int:
    return int(time.time())
