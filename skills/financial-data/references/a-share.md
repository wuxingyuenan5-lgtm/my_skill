# A股数据总入口

A股部分采用“总入口 + 专题手册”的结构。先在 `capability-index.yaml` 按数据集查状态，再读对应专题。

## 专题

- `a-share-market-data.md`：quote、K线、盘口/逐笔、指数/ETF、全市场横截面、代码/市场歧义。
- `a-share-fundamentals.md`：财务三表、F10、公告、公司资料、研报、一致预期。
- `a-share-flows-positioning.md`：资金流、两融、龙虎榜、大宗、股东户数、解禁、分红、板块资金。
- `a-share-microstructure.md`：涨停/炸板/跌停、昨日涨停、连板、监控、异动、热榜/人气。
- `a-share-research-news.md`：新闻快讯、互动易、题材/研究 workflow。
- `a-share-source-recipes.md`：mootdx、Tencent、Sina、Eastmoney、CNINFO、交易所、THS、iwencai、Wind/Choice 速查。

## 当前共享 Runtime

Tencent A股 quote/price/turnover/turnover_rate/market_cap/float_market_cap/PE/PB 为 `READY`；Sina 为独立 quote/price fallback。其余大量能力以 `RECIPE`/`RESTRICTED` 形式进入手册，供项目初始化时复制固化。

## 必须长期保留的坑点

- `000001` 等 symbol 存在市场歧义，显式 exchange 优先。
- Tencent 43=振幅、44=流通市值、45=总市值、46=PB；不要沿用旧教程错误映射。
- 北交所老 43/83/87 号段可能 HTTP 200 仍返回冻结数据，需解析现行 920xxx 代码。
- Eastmoney 风控与不同子域 WAF 分离；统一节流但 health 也要按域名隔离。
- 官方行业分类（申万/中信等）与供应商概念标签是不同 semantic field。
