# financial-data

Version: **0.1.0**

A reusable financial-data foundation for Agents: resolve instruments, choose sources by field, fetch, normalize, validate, retain provenance, fall back across independent providers, and compute reproducible derived metrics.

## Architecture

```text
Agent / research workflow
        ↓
DataRequest
        ↓
Instrument Master → field-level Router → Source Adapter(s)
        ↓                         ↘ independent fallback / cross-check
Normalize → Validate → DataPoint/DataResult → compact/standard/full output
```

The Skill entrypoint stays small. Long rules live in `references/`; executable code is a Python package in `scripts/financial_data/`; deterministic tests use local fixtures.

## Implemented in v0.1.0

- Unified `DataRequest` / `DataPoint` / `DataResult` contracts and explicit error codes.
- Instrument normalization for common A-share, HK, US equity/index and US Treasury aliases, including ambiguity guards.
- Source registry, source-health state, field-level routing, compliance filters and independent fallback ordering.
- Normalization/validation, cross-source tolerance checks, explicit `SOURCE_CONFLICT`, and compact/standard/full output profiles.
- Pure-Python returns, SMA/EMA, RSI, MACD, Bollinger, volatility, drawdown, percentile, turnover rate, turnover concentration, market breadth and KDJ.
- **Tencent**: CN quote/price/turnover/turnover rate/market cap/float market cap/PE/PB.
- **Sina**: independent CN quote/price fallback.
- **SEC EDGAR**: ticker→CIK, filing metadata, XBRL fundamentals including revenue, net income, operating cash flow, assets, liabilities and R&D expense.
- **US Treasury**: yield curve, 2Y, 10Y and derived 10Y–2Y spread.
- Orchestration workflows: stock snapshot, peer dataset, macro snapshot, filing-event dataset and local market-breadth calculation.

## Registry / reference only

The registry already models **Eastmoney, CNINFO, SSE/SZSE, CFTC, Yahoo Finance, CBOE and FINRA**, plus future fields such as sector rotation, COT, options/Greeks/IV, short volume, SEC Frames cross-sectional screening and richer K-line/market-wide data. They are **not claimed as executable v0.1.0 adapters** unless listed above.

This separation is intentional: source knowledge can be reviewed before an adapter is activated, without making the Agent pretend planned coverage is live capability.

## Install / use

Core runtime targets Python **3.9+** and requires `requests`.

```bash
pip install requests
export PYTHONPATH="$PWD/skills/financial-data/scripts:$PYTHONPATH"
```

Example:

```python
from financial_data import DataRequest, get_data, result_dict

r = get_data(DataRequest("600519", "quote", require_crosscheck=True))
print(result_dict(r, "compact"))
```

SEC automated access requires a truthful contact identity:

```bash
export SEC_CONTACT="Your Name your.email@example.com"
```

`SEC_CONTACT` is deliberately never hard-coded in the repository.

## Example task patterns

- “获取贵州茅台当前行情并用独立源复核价格与成交额。” — executable in v0.1.0 where comparable fallback fields exist.
- “获取 AAPL 最新 10-Q 的收入、净利润和经营现金流，附 filing date、report period、XBRL tag 和来源。” — executable through SEC EDGAR.
- “获取美债 2Y、10Y，并计算 10Y-2Y。” — executable through US Treasury.
- “比较宁德时代、比亚迪、亿纬锂能最新估值与盈利增速。” — quote valuation fields are partly executable; earnings-growth coverage requires additional adapters and must return `FIELD_NOT_SUPPORTED` instead of fabrication.
- “获取贵州茅台过去 250 个交易日日线并计算 20/60/120 日均线。” — local MA calculation exists; a production K-line adapter is a later minor-version item.
- “构建昨日 A 股申万行业涨跌和成交占比数据集。” — schema/workflow is defined; market-wide sector adapter is not yet executable in v0.1.0.

## Data guarantees

A standardized observation records its instrument, field/value/unit, relevant currency and dates, `source_id`, `as_of`, `retrieved_at`, status/quality flags, and optional provider/algorithm metadata. Percentages are stored as decimals. A source outage is never represented as an empty successful result.

For point-in-time research, publication/filing time is distinct from report period. For prices, adjustment convention must be explicit; for volume-like fields, distinguish shares/lots/contracts.

## Compliance

Source access and data rights are separate questions. The registry records commercial-use and redistribution posture, but those classifications can change; re-check the current source terms before commercial deployment. The Skill does not bypass CAPTCHA, access controls, robots restrictions, or explicit anti-scraping rules.

## Attribution

Architecture and source-discovery research were informed by the Apache-2.0 projects **`simonlin1212/a-stock-data`** and **`simonlin1212/global-stock-data`**. This repository uses a new modular implementation rather than copying their large embedded `SKILL.md` code wholesale. If substantive upstream code is imported in a future version, retain the applicable Apache-2.0 notices and source attribution.

## Test

```bash
pip install pytest
python -m pytest skills/financial-data/tests -q
python3 scripts/validate_skills.py
```
