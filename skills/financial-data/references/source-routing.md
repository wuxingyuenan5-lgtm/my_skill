# Source Routing

Routing is **field-level and usage-level**. There is no globally “best financial website” or provider.

## Decision inputs

- requested field/dataset
- market/instrument
- research vs commercial usage
- interactive/small query vs broad historical/batch workload
- provider health
- authority, reliability, freshness and compliance
- authentication/entitlement availability
- adapter/access-path availability
- independence from the failed/primary source

Generic score:

```text
30% Authority + 25% Reliability + 20% Freshness + 15% Compliance + 10% Health
```

Grades A/B/C/D map to 1.00/0.75/0.50/0.25. Narrow field/usage overrides sit above generic scoring.

## Current overrides

- US filings/XBRL/standard company facts → SEC EDGAR.
- US Treasury yield curve/2Y/10Y/spread → US Treasury.
- CN filings/original disclosure facts → CNINFO/SSE/SZSE/BSE before aggregators.
- CN quote/price, no-key lightweight research → Tencent → Sina → Eastmoney registry fallback.
- CN turnover/market cap/PE/PB, no-key research → Tencent before Eastmoney.
- CN structured A-share API/Agent access when an authenticated provider is acceptable → HiThink Finance is a first shortlist alongside licensed vendors.
- CN structured financial statements/latest valuation → HiThink Finance for normalized access; cross-check material conclusions against original filings when source-of-record matters.
- CN call auction → HiThink Finance first among currently modeled structured APIs; broker/Level-2 feed when order-level or stronger production guarantees are required.
- CN limit-state/anomaly/hot-list/dragon-tiger data → HiThink Finance and Eastmoney are separate vendor candidates; exchange sources remain authoritative for regulatory definitions/disclosures.
- CN public funds → issuer/fund-company/exchange for source-of-record disclosures; HiThink Finance for broad normalized API access; Wind/Choice for institution-grade licensed history where appropriate.
- CN full-market long-history A-share research → prefer HiThink market dump/Parquet or another bulk licensed dataset over thousands of per-symbol HTTP calls.
- THS public web/iwencai consensus/research capabilities remain separate from HiThink Financial API unless the current API contract exposes an equivalent endpoint.

An override is not permission to use a broken/blocked source. Health, entitlement and compliance filters still apply.

## Scale-aware routing

Do not route the same way for one symbol and an entire market.

```text
single/few instruments
→ normal provider endpoint

large universe / long history
→ batch endpoint or market dump
→ local Parquet/DuckDB
→ compute derived panels locally
```

A provider with a good per-symbol endpoint may still be the wrong route for a 5,000-stock historical job.

## Commercial mode

When `request.params["usage"] == "commercial"`, candidates not explicitly marked commercial-use `allowed` are removed. If sources exist but none qualifies, return `COMPLIANCE_RESTRICTED`, not `FIELD_NOT_SUPPORTED`.

An open-source client/repository license does not automatically grant redistribution rights to the underlying market data.

## Adapter/access-path availability

The router can know about a source whose shared adapter is not implemented. The facade skips non-executable routes and eventually returns an explicit unsupported/unavailable error; documentation must clearly separate registry coverage from executable coverage.

For HiThink Finance specifically, this Skill records provider/recipe knowledge but does not vendor the upstream CLI/SDK or make it a mandatory runtime dependency. Downstream projects may choose REST, MCP, CLI, Python or market-dump access and freeze only the selected path locally.
