---
name: financial-data
description: Use when a task needs financial-market data sources, retrieval recipes, normalization, source routing, provenance, fallback, project-local data modules, TradingView visualization, or reproducible derived metrics across equities, futures, options, rates, macro, FX or crypto.
---

# financial-data

## Purpose

Use this Skill as a **financial-data engineering handbook and reusable source library**.

Its job is broader than running one shared data API. It should answer:

- where a financial dataset should come from;
- how to retrieve it;
- what the fields/units/time semantics mean;
- which source should be primary and which should be fallback;
- what authentication, rate limits, terms and provider quirks matter;
- how to normalize/validate the result;
- how to copy the chosen recipe into a downstream project so that project can operate independently afterward;
- how to expose the resulting data to visualization layers such as TradingView.

Core chain: **Identify → Route → Fetch → Normalize → Validate → Cite → Export/Deliver**.

## Operating contract

1. Resolve the instrument before fetching. Prefer canonical identifiers; never guess an ambiguous symbol.
2. Route by **asset class + market + field + usage**, not by a global favorite website.
3. Every successful datum should retain provenance: `source_id`, `as_of`, `retrieved_at`, field/unit, and applicable currency/period/adjustment metadata.
4. Percentages are decimals internally; volume units, contract units and price-adjustment conventions must be explicit.
5. For supplier-derived or decision-critical data, cross-check an independent source when appropriate. A material disagreement is `SOURCE_CONFLICT`; preserve both observations rather than silently selecting one.
6. Fallback should prefer another domain/rate-limit plane. A provider failure is not equivalent to “no data.”
7. Check compliance/access conditions before commercial use or redistribution. Never bypass CAPTCHA, access controls or explicit anti-bot restrictions.
8. Compute deterministic derivatives locally where practical and record methodology/parameters.
9. Preserve detailed endpoint recipes, field mappings, known issues and confirmed-dead-source history when they have engineering value. Do not remove useful detail merely to keep the Skill small.
10. When a downstream project needs recurring data, prefer **project extraction**: copy only the required source adapters/contracts into that project instead of making every refresh depend on this Skill. See `references/project-export.md`.

## Capability status

Use these labels in the handbook:

- `READY`: reusable shared adapter exists.
- `RECIPE`: complete copy-ready source recipe exists; shared facade integration is optional.
- `RESTRICTED`: recipe is complete but requires key/license/permission/paid feed.
- `DEGRADED`: known upstream issue; fallback required.
- `DEPRECATED`: historical reference only.

A useful capability does **not** need to live behind the common facade to belong in this Skill. A complete, reliable recipe is sufficient for project extraction.

## Runtime

Reusable common Python lives under `scripts/financial_data/`. Add the Skill `scripts/` directory to `PYTHONPATH`, then:

```python
from financial_data import DataRequest, get_data, result_dict

result = get_data(DataRequest("600519", "quote", require_crosscheck=True))
print(result_dict(result, "compact"))
```

The facade is one convenience layer, not the only way to use this Skill.

## Reference routing

### Discovery

- Machine-readable capability catalog: `references/capability-index.yaml`

### Core engineering

- Data contract and provenance: `references/data-contract.md`
- Market/time/unit conventions: `references/market-conventions.md`
- Instrument identity: `references/instrument-master.md`
- Source registry/routing/health/fallback: `references/source-registry.md`, `references/source-routing.md`, `references/fallback-policy.md`
- Validation: `references/validation-rules.md`
- Compliance: `references/compliance.md`
- Reusable workflows: `references/workflows.md`
- Project extraction / one-time project setup: `references/project-export.md`

### Asset classes / markets

- A-shares: `references/a-share.md`
- US / HK equities: `references/us-hk.md`
- Macro / rates: `references/macro-rates.md`
- Futures / commodities / contract curves / warehouse / positioning: `references/futures-commodities.md`
- Options / derivatives: `references/derivatives.md`

### Visualization

- Canonical chart payloads independent of renderer: `references/chart-data-contract.md`
- TradingView Widgets / Advanced Charts / Datafeed API / UDF / Lightweight Charts / own-data chart format: `references/tradingview.md`

## Futures rule

Futures are a first-class domain. Never collapse exact contracts, dominant contracts and continuous series into one symbol concept. Contract lifecycle, settlement, night sessions, roll methodology, open interest, warehouse/position data and exchange parameters require explicit metadata.

## TradingView rule

Do not call everything a “TradingView API.” Distinguish:

- Widgets: TradingView-supplied market data embedded directly;
- Advanced Charts: TradingView chart UI using the project's own datafeed;
- Lightweight Charts: open-source chart rendering using project-supplied data;
- Trading Platform/Broker API: trading integration;
- Pine Script on tradingview.com: separate indicator environment.

TradingView is primarily a visualization/integration layer in this Skill, not an unofficial generic market-data scraping source.
