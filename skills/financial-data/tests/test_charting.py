from datetime import datetime, timezone
from financial_data.charting import normalize_resolution, to_lightweight_bar, to_tradingview_bar, to_udf_history

def test_tradingview_daily_bar_uses_trade_date_midnight_utc_ms():
    row={"trade_date":"2026-08-15","open":10,"high":12,"low":9,"close":11,"volume":100}
    bar=to_tradingview_bar(row,daily=True)
    assert bar["time"]==int(datetime(2026,8,15,tzinfo=timezone.utc).timestamp()*1000)

def test_tradingview_intraday_bar_uses_utc_milliseconds():
    row={"timestamp":"2026-08-15T09:30:00+08:00","open":1,"high":2,"low":1,"close":2}
    assert to_tradingview_bar(row)["time"]==int(datetime(2026,8,15,1,30,tzinfo=timezone.utc).timestamp()*1000)

def test_udf_history_sorts_and_uses_unix_seconds():
    rows=[{"timestamp":"2026-08-15T09:31:00+08:00","open":2,"high":3,"low":1,"close":2.5,"volume":20},{"timestamp":"2026-08-15T09:30:00+08:00","open":1,"high":2,"low":0.5,"close":1.5,"volume":10}]
    out=to_udf_history(rows); assert out["s"]=="ok"; assert out["t"]==sorted(out["t"]); assert out["o"]==[1.0,2.0]; assert out["v"]==[10.0,20.0]

def test_lightweight_daily_uses_business_day_string():
    assert to_lightweight_bar({"trade_date":"2026-08-15","open":1,"high":2,"low":0.5,"close":1.5},daily=True)["time"]=="2026-08-15"

def test_resolution_normalization():
    assert normalize_resolution("5m")=="5"; assert normalize_resolution("1h")=="60"; assert normalize_resolution("4H")=="240"; assert normalize_resolution("1d")=="1D"
