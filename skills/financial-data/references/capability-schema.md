# Capability Index Schema

`capability-index.yaml` is the machine-readable table of contents for the `financial-data` handbook. Agents should search it before opening large reference files.

## Status

- `READY`: a runtime module/adapter is shipped in `scripts/financial_data/` and may be called directly.
- `RECIPE`: the handbook contains enough source, field, fallback and implementation guidance to copy into a downstream project, but no stable common runtime adapter is promised.
- `RESTRICTED`: implementation guidance exists, but use requires an API key, paid data entitlement, vendor license, repository access or other permission.
- `DEGRADED`: the source/recipe is temporarily unreliable or only partially useful. Prefer its fallback.
- `DEPRECATED`: retained only to explain historical code or migration; do not choose for new work.

## Required fields

```yaml
- id: cn_equity_quote
  asset_class: equity
  market: CN
  dataset: quote
  status: READY
  primary_sources: [tencent]
  fallback_sources: [sina]
  auth: none
  compliance: research_only
  reference: a-share-market-data.md
  runtime: financial_data.adapters.tencent:TencentAdapter
  last_verified: 2026-08-15
```

For `RECIPE`/`RESTRICTED`, `runtime` should be omitted or `null`. Never mark an entry READY just because a source is described in prose.

## Query pattern

1. Filter by `asset_class` + `market` + `dataset`.
2. Prefer `READY` when a shared runtime implementation is useful.
3. For a project being initialized, `RECIPE` may be preferable if it gives a more direct, domain-specific implementation.
4. For commercial/redistributed products, check `compliance.md` and the provider's current terms before freezing a source.
5. Copy only the selected recipes into the project; do not force the downstream project to depend permanently on this handbook.
