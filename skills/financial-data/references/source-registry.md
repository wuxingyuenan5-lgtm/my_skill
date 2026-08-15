# Source Registry

Registry status is evidence about a source, not a guarantee that an executable adapter exists.

| Source | Markets | Main modeled fields | Adapter v0.1.0 | Compliance posture | Independence group |
|---|---|---|---|---|---|
| Tencent | CN/HK/US | quote, price, turnover, valuation, kline | **Yes (CN quote subset)** | research-only / restricted redistribution | tencent |
| Sina | CN/HK/US | quote, price, kline, statements, fund flow | **Yes (CN quote subset)** | research-only / restricted redistribution | sina |
| Eastmoney | CN/HK/US | quote, fund flow, margin, block trade, research, sectors, limit state | No | research-only; strict throttling/risk | eastmoney |
| CNINFO | CN | filings | No | verify per use | cninfo |
| SSE/SZSE | CN | filings, dragon-tiger, watchlist | No | verify per use | cn_exchanges |
| SEC EDGAR | US | filings, XBRL/fundamentals, standard financial metrics | **Yes** | government/open; declared UA required | sec |
| US Treasury | US/Global | yield curve, 2Y, 10Y, 10Y-2Y | **Yes** | government/open | us_treasury |
| CFTC | US/Global | COT/positioning | No | government/open | cftc |
| Yahoo | US/HK/Global | quote, kline, options, fundamentals, news | No | research/personal restrictions | yahoo |
| CBOE | US | options, Greeks, IV, flow | No | official but license/approval constraints | cboe |
| FINRA | US | short volume | No | verify scripted/commercial use | finra |

The executable subset is intentionally narrower than source knowledge. Unsupported registry-only fields return `FIELD_NOT_SUPPORTED`; they must not be represented as live capability.

## Health states

`healthy`, `degraded`, `broken`, `blocked`, `deprecated`.

Runtime health is process-local in v0.1.0. One or two classified failures degrade a source; three consecutive failures mark it broken for routing in that process. A success resets transient failures. Durable status and `last_verified` are reviewed metadata, not automatically rewritten by a single request.

## Metadata fields

Each `SourceSpec` records domain(s), markets, fields, authority/reliability/freshness/compliance grades, commercial and redistribution posture, authentication, rate-limit policy, status, last verification, independence group, adapter name and notes.
