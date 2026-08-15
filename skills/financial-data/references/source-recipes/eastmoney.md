# Eastmoney Recipe Guide

Eastmoney is valuable because it exposes many market-wide and event datasets not present in simple quote APIs. Treat it as a provider family with multiple independent host/risk-control planes, not one endpoint.

## READY provider toolkit

The shared reusable layer is:

```python
from financial_data import EastmoneyClient

em = EastmoneyClient(min_interval=1.0)
```

It deliberately exposes **provider-level primitives**, not one giant canonical adapter:

```python
# reportName-driven datasets
rows = em.datacenter_query(
    "RPTA_WEB_RZRQ_GGMX",
    filter_str='(SCODE="600519")',
    sort_columns="DATE",
)

# Push2 cross-section
rank = em.market_stock_list("us_nasdaq", sort_field="f3", page_size=50)

# security discovery
hits = em.search_securities("Apple")
```

Why this boundary: margin trading, lockup, dragon-tiger, sector flow, research and limit pools all have different provider field semantics and change risk. They should share one throttled HTTP/client layer while each downstream project freezes its own dataset contract.

## Common families

- `datacenter-web.eastmoney.com/api/data/v1/get`: reportName-driven structured datasets.
- `push2.eastmoney.com/api/qt/clist/get`: market/board cross-sections.
- `push2his.eastmoney.com`: historical K-line/fund-flow families.
- `reportapi.eastmoney.com`: stock/industry research metadata/PDF identifiers.
- `searchapi.eastmoney.com/api/suggest/get`: security discovery.
- other news/list/static hosts: provider-specific event datasets.

## Reviewed reportName examples

| Dataset | reportName |
|---|---|
| margin trading detail | `RPTA_WEB_RZRQ_GGMX` |
| block trades | `RPT_DATA_BLOCKTRADE` |
| shareholder counts | `RPT_HOLDERNUMLATEST` |
| dividends/bonus shares | `RPT_SHAREBONUS_DET` |
| lockup expiry | `RPT_LIFT_STAGE` |

`RPT_LIFT_STAGE` upstream field changes previously broke old mappings; current recipes preserve `FREE_SHARES_TYPE`, `FREE_SHARES` and actually-floatable-share semantics rather than trusting old column names.

## Error semantics

The shared client distinguishes:

1. HTTP/network failure — handled by `HttpClient` as classified `SOURCE_UNAVAILABLE`, `SOURCE_BLOCKED`, `RATE_LIMITED`, etc.
2. Provider business failure — for example datacenter `success=false`/non-zero `code`, or Push2 non-zero `rc`; these are **not** returned as successful empty data.
3. Successful response with `result=None` where the family legitimately uses this for no rows — returned as an empty dataset with raw payload retained.
4. Parser/schema failure — classified as `NORMALIZATION_ERROR`.

Do not write project code that collapses all four into `[]`.

## Throttle

`EastmoneyClient` defaults to serialized `min_interval=1.0`. Keep one client/session per workflow where practical. Do not parallelize a full-market loop just because the endpoint has no API key.

Reference-repo incident history is useful here: tens of thousands of concurrent Push2 requests caused IP-level blocking lasting many hours, while `datacenter-web` remained available because different host families use different WAF/rate-limit planes. Preserve source health per domain family rather than marking all Eastmoney as globally dead.

For batch analytics, prefer:

```text
one cross-section request
→ local filtering/grouping
```

over:

```text
N stocks × M fields × per-stock request
```

## Push2 market list

Default normalized fields from the READY helper:

| Provider | Normalized |
|---|---|
| f12 | code |
| f14 | name |
| f2 | price |
| f3 | change_pct (decimal after /100) |
| f4 | change |
| f5 | volume |
| f6 | turnover |
| f7 | amplitude (decimal after /100) |
| f15/f16 | high/low |
| f17/f18 | open/previous_close |

`diff` can be list or ordinal-keyed dict; the helper normalizes both. It also preserves the original row as `raw`.

Current market aliases include NASDAQ (`m:105`), NYSE (`m:106`), US ETF (`m:107`), HK (`m:116`) and a research-oriented `cn_a` Push2 universe. The handbook does **not** label the latter as complete all-A coverage until BSE universe semantics are explicitly frozen and verified.

## Security search

The public suggest family uses `type=14` for global securities. The shared helper currently filters default results to provider market numbers 105/106/107/116. Provider code/market number are aliases only; resolve them into the project Instrument Master before recurring use.

## Research

`reportapi.eastmoney.com/report/list`: normalize A-share stock ticker to pure six-digit code before query. Industry research uses the same endpoint family with different query type/industry filters. PDF download recipes must retain required Referer/header behavior and copyright restrictions.

## Board/sector data

`clist` can return industry/concept/region lists, price breadth and fund-flow fields. Set explicit sort field (`fid`) rather than assuming server order. Vendor concept/region tags must not be presented as official industry classification.

## Limit-state data

Push2ex/static families cover limit-up, break-board, limit-down, previous-limit, watchlist/anomaly. These are provider structured views; exchange rules/official notices remain the definition layer.

## Compliance boundary

The existence of `EastmoneyClient` means “reusable research integration exists,” not “commercial redistribution is licensed.” Keep Eastmoney data marked research-only unless the target project has separately confirmed its rights.
