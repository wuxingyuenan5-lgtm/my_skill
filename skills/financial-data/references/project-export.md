# Project Extraction Protocol

This Skill is designed to be consulted during project setup. A downstream project should be able to extract only the data capabilities it needs and then operate independently.

## 1. Default behavior

When a user asks to make a financial-data dependency permanent inside another project, do not force that project to call `financial-data` on every refresh.

Instead:

1. identify the exact required datasets;
2. choose primary and fallback sources;
3. freeze field definitions and time/unit conventions;
4. export copy-ready code and configuration;
5. record source/endpoint provenance and known issues;
6. add project-local validation/smoke checks;
7. let the target project own the extracted module thereafter.

## 2. Export manifest

Every extracted pack should include a small manifest:

```yaml
pack_version: 1
created_from_skill: financial-data
created_at:
project_scope:
  - cn_equity_quote
  - sw_industry_snapshot
primary_sources:
fallback_sources:
field_contracts:
trading_calendar:
rate_limits:
auth_requirements:
compliance_notes:
last_source_verification:
```

## 3. Suggested output tree

```text
data/
  README.md
  sources.yaml
  contracts.yaml
  instruments.py
  calendar.py
  adapters/
  normalize.py
  validate.py
  smoke_check.py
```

Only create the modules needed by the target project.

## 4. Recipe completeness standard

A recipe is export-ready only when it states:

- what exact dataset it obtains
- primary source
- independent fallback if available
- endpoint/protocol
- request parameters
- authentication/headers/cookies
- rate-limit guidance
- response field mapping
- unit/currency/percentage conventions
- time semantics
- known provider quirks
- error/no-data distinction
- source health/last verification
- compliance/license caveat
- copy-ready implementation

## 5. Capability status

Use these labels:

- `READY`: official project adapter exists and can be copied/reused.
- `RECIPE`: complete documented implementation exists but is not required in the shared runtime.
- `RESTRICTED`: complete integration guidance exists but requires a key, paid feed, explicit permission or other access condition.
- `DEGRADED`: previously usable recipe has a known provider issue.
- `DEPRECATED`: keep only for historical migration context; do not use for new projects.

## 6. Do not over-export

If a project only needs:

- A-share daily bars
- SW industry membership
- daily turnover

then export only those modules and their dependencies. Do not copy the full handbook or all source adapters into the target project.

## 7. Pin methodology, not fragile endpoints

The target project should persist:

- canonical fields
- fallback order
- normalization rules
- methodology IDs
- validation tolerances

Raw webpage endpoints can change. Keep them in source adapters so replacements do not alter the rest of the project.

## 8. Freeze an instrument master subset

For a recurring project, create a project-local symbol map instead of resolving names every run.

Example:

```yaml
600519.SH:
  canonical_id: equity_cn_600519
  exchange: SSE
  currency: CNY
  provider_symbols:
    tencent: sh600519
    eastmoney: 1.600519
    tradingview: SSE:600519
```

Provider symbols are aliases and may change independently of the canonical ID.

## 9. Visual layer export

If the project needs charts, export visualization separately from data acquisition.

For TradingView integrations see `tradingview.md`.

Preferred separation:

```text
backend/data/
frontend/charts/
```

A source adapter should never format data directly for one chart library. Use a chart-specific transformation layer.

## 10. Maintenance handoff

After export, the target project should own:

- source checks
- parser fixtures
- credentials
- deployment configuration
- cache/database
- monitoring

`financial-data` remains the master handbook for discovering better sources or rebuilding a broken integration later.
