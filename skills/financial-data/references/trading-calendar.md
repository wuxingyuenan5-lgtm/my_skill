# Trading Calendar and Session Master

Every recurring market-data project should own a calendar/session layer.

## Required fields

exchange, timezone, trading_date, is_open, session segments, auction/pre/post sessions, holiday/early-close reason, night-session mapping, source/version.

## Futures

China night-session wall-clock date can precede exchange trading day. Preserve both timestamp and `trade_date`. Session schedules vary by product and may change around holidays.

## US/global

Respect daylight saving through IANA timezone data; do not hard-code UTC-4/-5. Early closes and exchange-specific holidays must be represented explicitly.

## Chart integration

TradingView `session`/`timezone` and backend bar alignment should be generated from the same project calendar/session master where possible.
