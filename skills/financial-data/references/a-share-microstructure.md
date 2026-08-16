# A股涨跌停、异动、情绪与微观结构

## 核心池

- 涨停池：连板数、N日M板、封单金额、首次/最后封板、开板次数、行业。
- 炸板池：涨停打开后的股票、振幅/速度/回封。
- 跌停池：封单、连续跌停、开板次数。
- 昨日涨停池：今日表现、晋级/断板。
- 同花顺涨停原因/题材等 vendor/editorial 标签。
- 重点监控/风险警示池。
- 严重异常波动/日内异动池与规则码。

## 来源层级

交易所官方规则与披露用于事实/定义；Eastmoney push2ex/静态池用于结构化市场池；THS 用于涨停原因、概念/题材归因等 vendor 标签。

## 市场情绪快照

建议每日派生固定指标：`limit_up_count`、`limit_down_count`、`break_board_count`、`break_rate = break_board/(limit_up+break_board)`、`highest_board`、2/3/4/5+板梯队、昨日涨停平均收益、晋级率。比率均为 decimal，并记录算法版本。

## 重点监控与异常波动

监控池和严重异常波动是不同事件，不要合成一个风险标签。部分供应商异动 endpoint 即使 HTTP 200 也可能返回业务错误；必须检查业务状态。规则码保存 raw code + canonical explanation。

## 热榜/人气/概念命中

THS 热榜、Eastmoney 人气和概念命中均标 `sentiment/vendor_tag`，不能与申万正式行业分类混用。保存 rank、rank_change、heat、concept tags、as_of、vendor methodology。
