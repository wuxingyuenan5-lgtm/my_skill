# financial-data

Version: **0.3 encyclopedia-first**

A cross-asset **financial-data acquisition encyclopedia** for Agents: dataset maps, provider/API constraints, source recipes, methodology notes, and verified copy-ready reference implementations.

The intended lifecycle is simple:

**consult once → choose the required data/source → copy/freeze the recipe and rules into the downstream project → let that project own recurring updates.**

Shared runtime exists as verified reference implementations and copy-ready utilities. **Downstream projects are not expected to depend on this Skill at runtime** after selected source logic has been frozen into the project.

## Start here

1. Read `NAVIGATION.md`.
2. Classify the request as a research task, concrete dataset, named provider/API, or maintenance/audit question.
3. Open one first-hop card.
4. Only open provider/reference files for the sources actually shortlisted.
5. Freeze the selected source logic, field semantics, constraints and tests into the downstream project.

### Default read budget

Do not scan the whole Skill for a narrow question. A normal lookup should usually need only:

```text
SKILL.md
→ NAVIGATION.md
→ one task OR dataset card
→ one or two shortlisted provider cards
```

Typical total: **3-5 small files**. `references/capability-index.yaml` is no longer the ordinary first-read document; it is for coverage/maintenance audits.

## Encyclopedia layers

### `tasks/` — start from the research question

Examples: A股均线、市场宽度、期货期限结构、期货席位、碳酸锂、铜、跨资产研究、美股基本面。

Each task card answers: what data is required, what is optional, which dataset cards to open, what methodology matters, and what must be frozen locally.

### `datasets/` — define the dataset before choosing a source

Examples: A股K线、A股横截面、行业分类、国内期货真实合约行情、会员持仓排名、仓单/库存、交易参数、US/HK K线、SEC filings/companyfacts、Treasury rates、CFTC COT、Crypto exchange market data。

Each dataset card defines canonical fields, timing, units, source shortlist and source-selection pitfalls.

### `providers/` — source/API encyclopedia

Each provider card uses the same constraint structure:

- Identity / source-of-record status
- Access and authentication
- Technical request limits
- Data-range limits
- Freshness and publication timing
- Licensing and redistribution
- Data-quality limitations
- Copy guidance

Exact rate limits and access rules are only stated as official when current provider documentation supports them. Otherwise the card says `unknown` and keeps empirical safe-use advice separate. Volatile constraints carry `last_verified`.

Current first-pass provider cards cover Tencent, Eastmoney, Sina, CNINFO, SHFE, INE, DCE, CZCE, CFFEX, GFEX, Yahoo, SEC EDGAR, U.S. Treasury, CFTC, Binance, Wind/Choice and TradingView.

## Why the global Capability Index still exists

`references/capability-index.yaml` remains useful for:

- whole-Skill coverage audits;
- READY/RECIPE/RESTRICTED inventory;
- validator/maintenance work;
- migration/history.

It is deliberately **not** the normal acquisition-query entrypoint because reading a global index and then every possible provider wastes tokens and encourages over-engineering.

## Coverage

The encyclopedia covers A-shares, US/HK/global equities, SEC, futures/commodities, options, macro/rates, funds/ETF, FX/Crypto, reference data, TradingView/custom charts and professional licensed sources.

Existing detailed pages under `references/` remain available as deeper second/third-hop material. v0.3 does not duplicate or migrate every historical handbook page; the new cards point to them only when needed.

## Verified reference implementations — optional, not the center

`scripts/financial_data/` keeps tested reference code for selected sources and transformations:

- Tencent A-share quotes/K-lines
- Sina fallback quotes
- Yahoo v8 Chart K-lines
- Eastmoney market/search/datacenter toolkit
- SEC EDGAR / Frames / daily index helpers
- U.S. Treasury
- CFTC
- SHFE/INE/DCE/CZCE/CFFEX/GFEX exact-contract daily futures data
- SHFE/DCE/CZCE/CFFEX/GFEX member-positioning reference fetchers; INE parser/recipe remains transport-unfrozen
- futures dominant/term-structure/basis utilities
- TradingView/UDF/Lightweight chart transforms

A project can copy, simplify, rename, adapt or replace these implementations. What must survive is the dataset meaning, source/provenance, field/unit/timing rules, provider constraints, fallback logic and project-local tests.

## A few concrete lookup examples

### “我要A股日K做均线策略”

```text
NAVIGATION.md
→ tasks/a-share-ma-strategy.md
→ datasets/cn-equity/kline.md
→ providers/tencent.md
```

Only compare Sina/Eastmoney/Wind/Choice if the primary source does not fit the actual requirement.

### “我要碳酸锂期货持仓排名”

```text
NAVIGATION.md
→ datasets/futures/member-position-ranking.md
→ providers/gfex.md
```

Then copy the GFEX recipe/reference implementation into the lithium-carbonate project.

### “东财接口有什么限制？”

```text
NAVIGATION.md
→ providers/eastmoney.md
```

No A-share/futures/SEC/global scan is required.

### “整个 Skill 有哪些 READY 能力？”

This is maintenance/audit intent, so it is appropriate to open `references/capability-index.yaml`.

## Core correctness rules

- Never guess ambiguous symbols or units.
- Preserve source, as-of/retrieval time, currency/unit and trade/report/publish/available dates.
- Keep official facts, vendor-derived values, estimates/editorial tags and local calculations separate.
- Provider failure is not “no data.”
- Exact futures contracts, dominant contracts and continuous series are different objects.
- Settlement and close are different fields.
- Futures member Top-N rankings are disclosure subsets, not full-market net positions.
- Historical research needs point-in-time availability, not today's cleaned snapshot retroactively applied to the past.
- Do not bypass CAPTCHA/WAF/access controls.
- Public accessibility does not automatically grant commercial redistribution rights.

## Project extraction

After choosing a source, freeze into the downstream project at minimum:

- canonical instrument/data identity;
- chosen primary/fallback provider;
- endpoint/report family and relevant date regime;
- auth/config pattern without secrets;
- canonical fields and units;
- publication/trading-time semantics;
- provider limit/backoff rules;
- a small raw fixture or smoke check;
- `last_verified` for unstable endpoints;
- project-local methodology and tests.

See `references/project-export.md` for the deeper extraction checklist.

## Maintenance

When extending the encyclopedia, add the smallest useful route/card first. Do not automatically turn a new dataset into a shared adapter/facade. Promote code into a verified reference implementation only when reuse and silent-error prevention justify it.
