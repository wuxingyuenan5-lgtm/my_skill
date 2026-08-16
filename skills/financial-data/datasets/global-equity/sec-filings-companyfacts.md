# Dataset: SEC Filings / Companyfacts

## What this dataset means
SEC EDGAR公司提交文件、filing metadata和XBRL companyfacts/frames等官方披露数据。

## Common analytical uses
财报、公告事件、标准化财务指标、历史披露/PIT研究。

## Minimum canonical fields
`cik, accession, form, filing_date, accepted_at/available_at, report_period, concept, unit, value, source_url`。

## Frequency and timing semantics
事件驱动；区分报告期、提交日、accepted/published/available时间。修订文件可能改变后续可见事实。

## Recommended sources
`../../providers/sec-edgar.md`。

## Alternatives / licensed alternatives
公司IR、交易所公告、授权财务数据库；vendor标准化字段属于二次加工。

## Methodology and unit caveats
XBRL concept/company extension、单位、累计/单季口径需显式映射。回测不要用今天下载的最新companyfacts替代历史当时可获得数据。

## Source-selection pitfalls
CIK/ticker映射会变化；amendment、restatement和重复facts需要去重/PIT规则。

## Provider cards
`../../providers/sec-edgar.md`。

## Copy-ready references
`../../references/sec-edgar-advanced.md`, `../../references/global-equity-fundamentals.md`; runtimes `../../scripts/financial_data/adapters/sec_edgar.py`, `../../scripts/financial_data/sec_official.py`。