# Source Routing

Routing is **field-level**. There is no globally “best financial website.”

## Decision inputs

- requested field
- market/instrument
- research vs commercial usage
- provider health
- authority, reliability, freshness and compliance
- adapter availability
- independence from the failed/primary source

Generic score:

```text
30% Authority + 25% Reliability + 20% Freshness + 15% Compliance + 10% Health
```

Grades A/B/C/D map to 1.00/0.75/0.50/0.25. Narrow field overrides sit above generic scoring.

## v0.1.0 overrides

- US filings/XBRL/standard company facts → SEC EDGAR.
- US Treasury yield curve/2Y/10Y/spread → US Treasury.
- CN quote/price → Tencent → Sina → Eastmoney registry fallback.
- CN turnover/market cap/PE/PB → Tencent before Eastmoney.
- CN filings → CNINFO/SSE-SZSE before aggregators (adapters pending).

An override is not permission to use a broken/blocked source. Health and compliance filters still apply.

## Commercial mode

When `request.params["usage"] == "commercial"`, candidates not explicitly marked commercial-use `allowed` are removed. If sources exist but none qualifies, return `COMPLIANCE_RESTRICTED`, not `FIELD_NOT_SUPPORTED`.

## Adapter availability

The router can know about a source whose adapter is not implemented. The facade skips non-executable routes and eventually returns an explicit unsupported/unavailable error; documentation must clearly separate registry coverage from executable coverage.
