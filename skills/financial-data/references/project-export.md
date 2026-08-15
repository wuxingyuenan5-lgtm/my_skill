# Project Extraction Protocol

`financial-data` is normally consulted during project setup. The downstream project should extract only required capabilities and then operate independently.

## Workflow

1. Search `capability-index.yaml` and select exact capability IDs.
2. Choose primary + independent fallback sources.
3. Freeze canonical field definitions, units, timezone/trading-day, adjustment/methodology rules.
4. Copy only required provider recipes/runtime helpers/assets.
5. Add project-local parser fixtures, validation and source-health checks.
6. Record `last_verified`, provider terms and upstream attribution.
7. The target project owns refreshes, credentials, cache/database and monitoring afterward.

## Programmatic manifest

```python
from financial_data.project_export import build_project_manifest, render_manifest_markdown

manifest = build_project_manifest(
    capability_index,
    ["cn_equity_quote", "futures_term_structure", "chart_lightweight_transform"],
    project_name="market-dashboard",
)
print(render_manifest_markdown(manifest))
```

The helper deliberately does not download proprietary/restricted libraries or credentials. It tells the project what needs to be copied/authorized.

Template: `assets/project-data-pack/README.template.md`.

## Suggested output

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
frontend/
  charts/
README.md
```

## Export-ready recipe checklist

Exact dataset; primary/fallback; endpoint/protocol; request params; auth/headers/cookies; rate limit; response field map; unit/currency/percent rules; time semantics; provider quirks; error-vs-no-data; source health/verification date; compliance/license; copy-ready implementation.

## Instrument subset

Freeze provider aliases per canonical instrument, for example:

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

## Visualization separation

Keep `backend/data/` separate from `frontend/charts/`. Source adapters never emit renderer-specific payloads directly; transform canonical bars through `financial_data.charting`.

## Maintenance handoff

When a provider breaks, return to the handbook, choose another recipe, dual-run if possible, update field/fallback mapping, then freeze the replacement into the downstream project. Do not solve recurring breakage by making the project depend permanently on handbook execution.
