# Dataset: A股行业分类

## What this dataset means
证券在某一分类体系、版本和有效日期下的行业归属，不是永恒静态标签。

## Common analytical uses
行业涨跌/成交额、行业中性、板块扩散度、历史归因和股票池分组。

## Minimum canonical fields
`instrument_id, taxonomy, taxonomy_version, level, industry_code, industry_name, effective_from, effective_to, source_id`。

## Frequency and timing semantics
分类调整是事件驱动；历史研究必须使用当时有效成员关系。

## Recommended sources
优先使用所选分类体系的官方/授权成员表；申万等商业分类需确认许可。Wind/Choice可作为机构环境映射来源。

## Alternatives / licensed alternatives
交易所行业、证监会分类、自定义映射，但不能与申万名称混用。

## Methodology and unit caveats
必须保存taxonomy与版本；同一公司可因时间和体系不同属于不同板块。历史回测避免用当前行业标签回填过去。

## Source-selection pitfalls
网络行情网站展示分类常用于展示/聚合，不一定提供完整PIT历史或分类许可。

## Provider cards
`../../providers/wind-choice.md`；公开供应商只能在确认具体分类来源后使用。

## Copy-ready references
`../../references/industry-classification.md`。