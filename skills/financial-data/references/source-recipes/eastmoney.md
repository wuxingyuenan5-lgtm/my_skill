# Eastmoney Recipe Guide

Eastmoney is valuable because it exposes many market-wide and event datasets not present in simple quote APIs. Treat it as a provider family with multiple independent host/risk-control planes, not one endpoint.

## Common families

- `datacenter-web.eastmoney.com/api/data/v1/get`: reportName-driven structured datasets.
- `push2.eastmoney.com`: quotes, clist/ulist/slist and board cross-sections.
- `push2his.eastmoney.com`: historical K-line/fund-flow families.
- `reportapi.eastmoney.com`: stock/industry research metadata/PDF identifiers.
- search/news/list hosts: security discovery and news/event lists.

## Reviewed reportName examples

| Dataset | reportName |
|---|---|
| margin trading detail | `RPTA_WEB_RZRQ_GGMX` |
| block trades | `RPT_DATA_BLOCKTRADE` |
| shareholder counts | `RPT_HOLDERNUMLATEST` |
| dividends/bonus shares | `RPT_SHAREBONUS_DET` |
| lockup expiry | `RPT_LIFT_STAGE` |

`RPT_LIFT_STAGE` upstream field changes previously broke old mappings; current recipes preserve `FREE_SHARES_TYPE`, `FREE_SHARES` and actually-floatable share semantics rather than trusting old column names.

## Throttle

Use one session per hostname/family. Serialise sensitive calls, apply minimum interval+jitter, exponential backoff on transient 429/5xx, and treat 403/empty-after-heavy-use as risk-control signals. Bulk workflows should request cross-sections once and filter locally rather than issuing one request per stock per field.

## push2 parser rules

`diff` may be a list or a dict keyed by ordinal. Normalize both. Validate business payload (`data`/`result`) before returning an empty result. Preserve f-field map/version in the project because vendor field IDs are not self-documenting.

## Research

`reportapi.eastmoney.com/report/list`: normalize stock ticker to pure six-digit code before query. Industry research uses the same endpoint family with different query type/industry filters. PDF download recipes must retain required Referer/header behavior and copyright restrictions.

## Board/sector data

`clist` can return industry/concept/region lists, price breadth and fund-flow fields. Set explicit sort field (`fid`) rather than assuming server order.

## Limit-state data

push2ex/static families cover limit-up, break-board, limit-down, previous-limit, watchlist/anomaly. These are provider structured views; exchange rules/official notices remain the definition layer.
