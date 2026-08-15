# Point-in-Time, Vintage and Revision Rules

For backtest/research correctness, distinguish when a fact describes the world from when the market could know it.

## Dates

- `trade_date`: exchange trading day.
- `calendar_date`: wall-clock date.
- `report_period`: accounting/economic period.
- `publish_date` / `published_at`: source publication.
- `accepted_at`: regulator receipt when available.
- `available_at`: earliest timestamp allowed by the project for historical use.
- `retrieved_at`: this system's fetch time.
- `revision_at` / `vintage_id`: macro/provider revision identity.

## Financial statements

Do not join quarterly values to period-end price as if known then. Use filing/publish/available time.

## Macro

Keep original release and later revisions where possible. A backtest using today's revised GDP/CPI history is not point-in-time unless explicitly intended.

## Constituents/classifications

Index membership, industry classification, shares outstanding, corporate actions and ticker mappings all need effective dates to avoid survivorship leakage.
