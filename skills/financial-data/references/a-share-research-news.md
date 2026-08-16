# A股新闻、互动、研究与事件数据

## 新闻/快讯

个股新闻可用门户聚合；财联社适合盘中/7x24 事件但接口签名和可用性可能变化；Eastmoney 全球财经快讯可作为不同域名备源。新闻标准字段：published_at、headline、summary、publisher、symbols、url、retrieved_at。搜索摘要不能代替正文来源。

## 互动易 / IRM

CNINFO 投资者互动适合回答“公司如何回应某传闻/产品/订单问题”。标准字段：question、answer、answerer、ask_time、answer_time（若有）、company、source_url。最新提问未回复是正常状态，`answer=null` 与接口失败必须区分。

## 热点与题材

THS hot stocks/hot list、Eastmoney popularity/concept hits 都属于供应商情绪/题材标签；用于策略时保存供应商和方法口径。

## 单标的初始化 workflow

1. quote/valuation；2. 最新公告与财务；3. 一致预期/研报；4. 正式行业 + 概念标签；5. 资金/龙虎榜/解禁/融资；6. 互动易/新闻；7. 将所选 source manifest 固化到项目。
