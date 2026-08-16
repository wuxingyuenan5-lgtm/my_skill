# financial-data Encyclopedia Navigation Restructure Design

## Context

`financial-data` has grown into a broad cross-asset financial-data handbook with provider notes, source recipes, methodology, capability metadata, and several verified reference runtimes. Its intended operating model is not a long-lived centralized SDK dependency: a downstream project should consult the Skill when it needs data, identify the smallest relevant dataset/source guidance, copy or freeze the selected recipe/implementation into the project, and then operate independently.

The current navigation still encourages agents to search the full `references/capability-index.yaml` first. As the encyclopedia grows, that default causes unnecessary full-index scans, broad provider enumeration, excess token use, and a bias toward engineering abstractions rather than answering the practical question: **what data do I need, where should I get it, what are the constraints, and what should I copy into my project?**

## Goal

Restructure `financial-data` into a token-efficient **financial data acquisition encyclopedia** with progressive disclosure:

1. route a user request to the smallest relevant knowledge block;
2. distinguish research-task navigation, dataset navigation, and provider navigation;
3. make provider/API access constraints explicit and standardized;
4. preserve existing verified runtimes as reference implementations rather than downstream runtime dependencies;
5. keep the global capability index for maintenance/audit, but remove it from the default query path.

## Non-goals

This phase does **not**:

- build a new data service, database, middleware layer, daemon, API server, or orchestration system;
- require downstream projects to import or call the Skill after project setup;
- make every dataset `READY`;
- rewrite all existing reference pages in one pass;
- move every existing file solely for directory aesthetics;
- add new market-data sources merely to increase coverage;
- perform broad live-provider revalidation unless required to document a provider constraint accurately.

## Core operating model

The canonical usage flow becomes:

```text
User need
  -> classify intent
     -> research task
     -> concrete dataset
     -> named provider/API
  -> open NAVIGATION.md
  -> open one task card OR one dataset card OR one provider card
  -> shortlist source(s)
  -> open provider card(s) only for shortlisted sources
  -> open copy-ready recipe/reference implementation only when needed
  -> freeze selected source rules/code into downstream project
  -> downstream project owns recurring updates; Skill is no longer required at runtime
```

The Skill is an encyclopedia consulted at design/setup time. Existing `scripts/financial_data/` code remains valuable as tested reference implementation and copy-ready source material, but it is not the conceptual center of the Skill.

## Navigation policy

### Default entrypoint

`SKILL.md` must direct agents to `NAVIGATION.md`, not to the full capability index.

### Intent priority

1. **Research-task intent** — e.g. "build an A-share moving-average study", "research lithium carbonate", "analyze futures term structure". Open one relevant task card first.
2. **Concrete dataset intent** — e.g. "A-share daily K-line", "futures member positions", "SEC company facts". Open one dataset card first.
3. **Named provider/API intent** — e.g. "Eastmoney API limits", "GFEX data", "Yahoo K-line". Open the named provider card directly.
4. **Maintenance/audit intent** — e.g. "what capabilities are covered", "which entries are READY". Only then use `references/capability-index.yaml` as a broad index.

### Default read budget

The Skill must explicitly instruct agents:

- Do not read `capability-index.yaml` in full by default.
- Do not enumerate every provider before shortlisting.
- Do not scan all domain reference pages for a narrow request.
- Start with `SKILL.md` + `NAVIGATION.md`.
- Open at most one task card or one dataset card initially.
- Open provider cards only for shortlisted sources.
- A normal lookup should usually finish within **3-5 small files total**.
- Expand beyond that only when the first route is insufficient or the task truly spans multiple datasets.

This is a progressive-disclosure rule, not a hard filesystem access control.

## Information architecture

The target structure is:

```text
skills/financial-data/
├─ SKILL.md
├─ NAVIGATION.md
├─ README.md
├─ tasks/
├─ datasets/
│  ├─ cn-equity/
│  ├─ futures/
│  ├─ global-equity/
│  ├─ macro/
│  ├─ options/
│  ├─ funds/
│  ├─ fx/
│  └─ crypto/
├─ providers/
├─ methodology/
├─ recipes/
├─ references/
└─ scripts/
```

For v0.3, only the high-value navigation layer and representative high-frequency cards need to be created. Existing domain references remain valid and are linked from the new cards instead of being migrated wholesale.

## NAVIGATION.md design

`NAVIGATION.md` must stay short enough to read on every Skill invocation. It should contain three compact routing tables.

### Task routes

First-pass task routes:

- A-share moving-average / technical strategy research -> `tasks/a-share-ma-strategy.md`
- A-share market breadth / turnover / market cross-section -> `tasks/a-share-market-breadth.md`
- China futures term structure / dominant-contract research -> `tasks/futures-term-structure.md`
- China futures member-positioning research -> `tasks/futures-positioning.md`
- lithium-carbonate futures research -> `tasks/lithium-carbonate-research.md`
- copper / commodity research -> `tasks/copper-research.md`
- cross-asset research / morning brief -> `tasks/cross-asset-research.md`
- US equity fundamentals / filings -> `tasks/us-equity-fundamentals.md`

Each route points to exactly one task card first.

### Dataset routes

First-pass dataset routes:

- CN equity daily/intraday K-line -> `datasets/cn-equity/kline.md`
- CN equity market cross-section -> `datasets/cn-equity/market-cross-section.md`
- CN equity industry classification -> `datasets/cn-equity/industry-classification.md`
- CN futures exact-contract daily market data -> `datasets/futures/daily-contract-market-data.md`
- CN futures member rankings -> `datasets/futures/member-position-ranking.md`
- futures warehouse/inventory -> `datasets/futures/warehouse-inventory.md`
- futures trading parameters -> `datasets/futures/trading-parameters.md`
- US/HK K-line -> `datasets/global-equity/kline.md`
- SEC filings/company facts -> `datasets/global-equity/sec-filings-companyfacts.md`
- Treasury/rates -> `datasets/macro/us-rates-treasury.md`
- CFTC positioning -> `datasets/macro/cftc-positioning.md`
- crypto exchange market data -> `datasets/crypto/exchange-market-data.md`

Each route points to one dataset card first.

### Provider routes

First-pass provider routes:

- Tencent -> `providers/tencent.md`
- Eastmoney -> `providers/eastmoney.md`
- Sina -> `providers/sina.md`
- CNINFO -> `providers/cninfo.md`
- SHFE -> `providers/shfe.md`
- INE -> `providers/ine.md`
- DCE -> `providers/dce.md`
- CZCE -> `providers/czce.md`
- CFFEX -> `providers/cffex.md`
- GFEX -> `providers/gfex.md`
- Yahoo -> `providers/yahoo.md`
- SEC EDGAR -> `providers/sec-edgar.md`
- US Treasury -> `providers/us-treasury.md`
- CFTC -> `providers/cftc.md`
- Binance -> `providers/binance.md`
- Wind / Choice -> `providers/wind-choice.md`
- TradingView -> `providers/tradingview.md`

Named-provider queries go directly to the matching provider card.

## Task-card contract

A task card answers: **what data do I need for this research?**

Required sections:

- objective / typical questions;
- required datasets;
- optional datasets;
- recommended source for each dataset;
- when to prefer a licensed source;
- methodology links;
- minimum project-local artifacts to freeze;
- explicit "do not load" guidance for unrelated domains when useful.

A task card should normally link to dataset cards, not duplicate all provider details.

## Dataset-card contract

A dataset card answers: **what is this dataset and which sources are appropriate?**

Required sections:

- dataset name and canonical meaning;
- common analytical uses;
- minimum canonical fields;
- frequency / timing semantics;
- recommended primary source(s);
- alternatives / paid alternatives;
- important methodology or unit caveats;
- known source-specific pitfalls that affect source selection;
- provider-card links;
- copy-ready recipe/reference runtime links when available.

Dataset cards should not copy full API-limit details for every provider; those belong in provider cards.

## Provider/API Source Constraint Card

Every provider card must contain a standardized constraint section. Unknown values must be written as `unknown` / `provider_not_committed`, not guessed.

Required fields/categories:

### Identity

- provider name;
- provider type: official exchange/regulator, public vendor, licensed vendor, broker/exchange API, chart platform, etc.;
- source-of-record status;
- best-use cases and poor-use cases.

### Access and authentication

- API key/token requirement;
- login requirement;
- cookie requirement;
- referer/user-agent/header requirement;
- IP restriction if known;
- WAF / CAPTCHA / automation-risk notes;
- prohibited behavior: never bypass CAPTCHA/access controls/explicit anti-bot restrictions.

### Technical request limits

Separate **officially published limits** from **recommended conservative operating limits**:

- official QPS/RPM/concurrency limit;
- recommended QPS/RPM/concurrency when official values are absent or looser than safe practice;
- maximum rows/page size if known;
- pagination behavior;
- batch endpoint availability;
- timeout/retry considerations;
- typical 403/429/blocking patterns.

A recommended safe rate must never be presented as an official provider limit.

### Data-range limits

- available frequencies;
- historical depth;
- endpoint-specific lookback caps;
- format/path regimes by date when relevant;
- symbol/universe coverage;
- retention limits for high-frequency data.

### Freshness and publication timing

- update frequency;
- typical publish/update time if known;
- safe collection time if empirically useful;
- intraday delay / near-real-time status;
- revision behavior;
- `last_verified` guidance for unstable public endpoints.

### Licensing and redistribution

- research suitability;
- commercial-use caveat;
- redistribution/derived-data restrictions where known;
- paid entitlement/licensed-terminal requirements;
- explicit instruction to verify current provider terms when rights are unclear.

### Data-quality limitations

- official/raw vs vendor-derived vs estimated/editorial;
- adjustment/revision semantics;
- units/currency quirks;
- known stale-symbol/field-map issues;
- survivorship / PIT caveats where relevant;
- whether independent cross-check is recommended.

### Copy guidance

- minimal recipe/reference implementation path;
- fields/config to freeze in downstream project;
- provider-specific smoke check to keep locally;
- fallback recommendation.

## Provider constraint accuracy policy

Provider limits and access rules can change. Therefore:

- exact current rate limits, endpoint caps, authentication requirements, historical limits, or commercial-use terms must be sourced from current official documentation/provider terms where available;
- if only empirical behavior is known, label it as empirical/recommended rather than official;
- if a current limit cannot be verified, record `unknown` rather than infer a number;
- volatile constraint facts should carry `last_verified` when practical;
- WAF behavior is recorded descriptively; the Skill must not contain bypass instructions for access controls.

## Existing capability-index role

`references/capability-index.yaml` remains machine-readable maintenance metadata for:

- coverage audits;
- READY/RECIPE/RESTRICTED inventory;
- validator checks;
- migration/history;
- maintainers who need a broad capability view.

It is no longer the default lookup path for ordinary dataset acquisition questions.

## Existing runtime role

Existing modules under `scripts/financial_data/` are retained. README and SKILL documentation must state clearly:

> Shared runtime exists as verified reference implementations and copy-ready utilities. Downstream projects are not expected to depend on this Skill at runtime after the selected data recipe/source logic has been frozen into the project.

No existing runtime is removed solely to make the encyclopedia more document-centric.

## v0.3 first-pass content

To prove the navigation model without rewriting the whole encyclopedia, v0.3 will create the cards referenced by the first-pass navigation routes.

### Initial task cards

1. `tasks/a-share-ma-strategy.md`
2. `tasks/a-share-market-breadth.md`
3. `tasks/futures-term-structure.md`
4. `tasks/futures-positioning.md`
5. `tasks/lithium-carbonate-research.md`
6. `tasks/copper-research.md`
7. `tasks/cross-asset-research.md`
8. `tasks/us-equity-fundamentals.md`

### Initial dataset cards

1. `datasets/cn-equity/kline.md`
2. `datasets/cn-equity/market-cross-section.md`
3. `datasets/cn-equity/industry-classification.md`
4. `datasets/futures/daily-contract-market-data.md`
5. `datasets/futures/member-position-ranking.md`
6. `datasets/futures/warehouse-inventory.md`
7. `datasets/futures/trading-parameters.md`
8. `datasets/global-equity/kline.md`
9. `datasets/global-equity/sec-filings-companyfacts.md`
10. `datasets/macro/us-rates-treasury.md`
11. `datasets/macro/cftc-positioning.md`
12. `datasets/crypto/exchange-market-data.md`

### Initial provider cards

1. `providers/tencent.md`
2. `providers/eastmoney.md`
3. `providers/sina.md`
4. `providers/cninfo.md`
5. `providers/shfe.md`
6. `providers/ine.md`
7. `providers/dce.md`
8. `providers/czce.md`
9. `providers/cffex.md`
10. `providers/gfex.md`
11. `providers/yahoo.md`
12. `providers/sec-edgar.md`
13. `providers/us-treasury.md`
14. `providers/cftc.md`
15. `providers/binance.md`
16. `providers/wind-choice.md`
17. `providers/tradingview.md`

The initial cards may point back to existing detailed reference pages instead of duplicating them.

## Validation strategy

This phase is documentation/navigation-centric. Validation should verify structure and routing rather than creating unnecessary runtime abstractions.

### Static validation

- `SKILL.md` no longer says to read full capability index first;
- `NAVIGATION.md` exists and remains compact;
- every first-pass route target exists;
- representative task cards link to valid dataset/provider/reference paths;
- each provider card contains all mandatory Source Constraint Card sections;
- no provider card labels an empirical recommendation as an official limit;
- no unresolved `TBD`/`TODO` placeholders;
- README states downstream projects do not require Skill runtime dependency.

### Scenario navigation tests

Manually/static-check representative lookups:

1. "A股日K做均线策略" -> `SKILL.md` -> `NAVIGATION.md` -> one task card -> one dataset card -> shortlisted provider card(s).
2. "碳酸锂期货持仓排名" -> `SKILL.md` -> `NAVIGATION.md` -> `datasets/futures/member-position-ranking.md` -> `providers/gfex.md`.
3. "东财接口有什么限制" -> `SKILL.md` -> `NAVIGATION.md` -> `providers/eastmoney.md`.
4. "整个Skill有哪些READY能力" -> maintenance/audit route -> capability index is allowed.

Ordinary narrow scenarios should not require a full capability-index scan.

## Versioning and branch rules

- Target documentation version: **v0.3 encyclopedia-first**.
- Work only on `feat/financial-data-skill`.
- Keep Draft PR #1 open.
- Do not merge or force-rewrite `main` without explicit authorization.

## Success criteria

v0.3 is successful when:

1. a narrow data-acquisition question can normally be routed with `SKILL.md + NAVIGATION.md + 1-3 relevant cards`;
2. `capability-index.yaml` is no longer the ordinary first-read document;
3. every first-pass route has a real target file;
4. provider/API constraints are standardized, explicit, and distinguish official limits from empirical safe-use recommendations;
5. existing detailed references and verified runtimes remain discoverable without becoming default reading;
6. downstream-project independence is explicit: consult once, copy/freeze what is needed, then operate locally.
