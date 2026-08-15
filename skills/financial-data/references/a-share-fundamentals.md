# A股基本面、F10、研报与一致预期

## 能力范围

财务三表与季度关键指标、F10/公司资料/股本结构、法定公告、个股与行业研报、机构一致预期 EPS/评级/目标价、分红与 corporate actions。

## 推荐路由

1. 交易所/巨潮公告是事实与披露时间的权威层。
2. 财报结构化读取可用 mootdx / Eastmoney / Sina 作为研究便利层。
3. 研报/一致预期属于供应商或券商研究层，不应和法定财报事实混为一类。

## 财报三表

### Sina statements

适合 HTTP 取资产负债表、利润表、现金流。项目应把原始中文科目映射到 canonical metric，并保留 `raw_field` 与 mapping version。例如营业收入→`revenue`、归母净利润→`net_income_parent`、经营现金流→`operating_cash_flow`。

### mootdx financial/F10

适合低依赖本地研究：财务快照 + F10 多类别。F10 体量大，先字段筛选/截断再进入 LLM；保留原始全文链接或缓存路径。

### Eastmoney datacenter/F10

适合结构化财务指标、股本、行业、证券资料。所有 Eastmoney HTTP 端点统一走 throttle/session；不要在全市场循环里高并发。

## CNINFO / exchange filings

公告至少保留 code/name、title/category、publish time、report period（若有）、PDF/source URL、source platform、retrieved_at。巨潮查询的 orgId 不应简单硬编码；上游曾因硬编码导致部分 601xxx 静默为空，可靠项目应先从官方证券映射解析 orgId。

## 研报

Eastmoney `reportapi.eastmoney.com/report/list`：个股研报调用前必须把 ticker 归一成纯 6 位；行业研报与个股研报共享 endpoint family，通过行业查询参数区分。PDF 下载要使用正确 header/Referer。

标准研报元数据：published_at、institution、analyst、title、rating、target_price、eps_fy1/fy2/fy3、source_url、pdf_url。

## THS consensus EPS / iwencai

同花顺一致预期可作 forward EPS/评级辅助；iwencai 主题检索若需 API Key/SkillHub 则标 `RESTRICTED`。一致预期是 vendor-derived，必须同时保存 `forecast_year`、`as_of` 和供应商方法口径，禁止与已披露实际 EPS 混用。
