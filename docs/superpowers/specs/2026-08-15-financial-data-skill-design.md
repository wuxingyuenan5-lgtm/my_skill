# financial-data Skill 设计规范

日期：2026-08-15
状态：设计冻结候选
目标仓库：`wuxingyuenan5-lgtm/my_skill`
目标目录：`skills/financial-data/`

## 1. 目标

构建一个可长期维护、可被 Codex/Claude Code/其他 Agent 复用的金融数据基础设施 Skill。它不是单纯的 API 接口合集，而是统一规定金融数据的：识别、路由、获取、标准化、校验、来源追踪、降级、压缩和交付。

核心链路：

`Identify -> Route -> Fetch -> Normalize -> Validate -> Cite -> Deliver`

优先参考并吸收：

- `simonlin1212/a-stock-data`：A 股多层数据能力、低封禁优先、独立备用源、研究工作流、Token 压缩。
- `simonlin1212/global-stock-data`：官方源优先、合规分级、SEC/Treasury/CFTC/FINRA/CBOE、跨市场数据能力。

不直接复制两个项目的大型单文件模式；如移植实质性代码，必须保留 Apache-2.0 许可与 attribution。

## 2. 方案比较与选择

### 方案 A：合并两个参考仓库为一个超大 `SKILL.md`

优点：最快、端点数量最多。

缺点：上下文巨大、Token 浪费、代码和规则混杂、维护困难、任何小改动都可能影响整个 Skill。

结论：不采用。

### 方案 B：按市场拆成 `a-stock-data` / `global-stock-data` 两个 Skill

优点：边界简单，接近上游结构。

缺点：数据契约、标的映射、校验和合规规则会重复；跨资产任务需要多个 Skill 协调；长期容易产生口径漂移。

结论：不采用为主架构，可在 references 内按市场拆模块。

### 方案 C：统一 `financial-data` 主 Skill + 模块化规范/适配器

优点：统一金融数据语义层；可以按市场/数据类型按需加载；易于测试和扩展；适合晨报、看板、回测、研究等多个上层项目复用。

缺点：初始设计工作更多。

结论：采用。

## 3. 目录结构

```text
skills/financial-data/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── data-contract.md
│   ├── instrument-master.md
│   ├── source-registry.md
│   ├── source-routing.md
│   ├── validation-rules.md
│   ├── market-conventions.md
│   ├── compliance.md
│   ├── fallback-policy.md
│   ├── workflows.md
│   ├── a-share.md
│   ├── us-hk.md
│   ├── macro-rates.md
│   ├── futures-commodities.md
│   └── derivatives.md
├── scripts/
│   ├── financial_data.py
│   ├── contracts.py
│   ├── instruments.py
│   ├── registry.py
│   ├── routing.py
│   ├── validation.py
│   ├── normalize.py
│   ├── indicators.py
│   ├── source_health.py
│   └── adapters/
│       ├── tencent.py
│       ├── eastmoney.py
│       ├── sina.py
│       ├── cninfo.py
│       ├── sse_szse.py
│       ├── sec_edgar.py
│       ├── treasury.py
│       ├── cftc.py
│       └── yahoo.py
└── tests/
    ├── test_contracts.py
    ├── test_instruments.py
    ├── test_routing.py
    ├── test_normalize.py
    ├── test_validation.py
    └── fixtures/
```

`SKILL.md` 保持轻量，只写触发条件、总原则、操作流程、必须遵守的质量门槛和 references 路由。具体接口参数、市场特殊规则和长表放入 references；可复用执行逻辑放 scripts。

## 4. 核心数据契约

所有标准化输出都必须带 provenance，不允许只返回裸数值。

最小标准记录：

```yaml
instrument_id: equity_cn_600519
symbol: 600519.SH
field: turnover
value: 6830000000
unit: CNY
currency: CNY
trade_date: 2026-08-14
as_of: 2026-08-14T15:00:00+08:00
source_id: tencent
source_type: secondary
retrieved_at: 2026-08-15T11:00:00+08:00
adjustment: none
status: verified
quality_flags: []
```

必须区分：

- `trade_date`：交易日。
- `calendar_date`：自然日。
- `report_period`：财报所属期。
- `publish_date`：公告/数据发布日期。
- `as_of`：数据在何时有效。
- `retrieved_at`：系统实际抓取时间。

价格必须声明复权口径：`raw / forward_adjusted / backward_adjusted / total_return_adjusted`。

数量必须显式单位：`shares / lots / contracts`。

百分比内部统一存储为小数，例如 3.21% -> `0.0321`，展示层再格式化。

## 5. Instrument Master

建立统一标的主数据，不允许各数据源各自解释 ticker。

最小字段：

```yaml
canonical_id: equity_cn_600519
symbol: 600519
exchange: SSE
ticker: 600519.SH
name_cn: 贵州茅台
asset_class: equity
currency: CNY
country: CN
aliases: []
external_ids: {}
```

目标覆盖资产类：

- Equity
- Index
- ETF
- Future
- Option
- FX
- Crypto
- Rates
- Macro Series

必须支持供应商代码映射，例如 ticker <-> SEC CIK、A 股交易所代码、港股补零规则等。

## 6. 数据分类

V1 数据语义层至少覆盖：

1. `market_data`：实时/延迟行情、OHLCV、盘口。
2. `fundamentals`：三表、关键指标、盈利预测。
3. `filings`：公告、10-K/10-Q/8-K、监管文件。
4. `valuation`：PE/PB/EV 类指标及其明确口径。
5. `ownership_positioning`：融资融券、大宗交易、股东户数、解禁、机构持仓、COT、short volume。
6. `market_microstructure`：涨跌停、炸板、连板、异常交易、订单簿。
7. `market_breadth`：上涨家数、涨停率、成交集中度等可复现派生数据。
8. `sector_classification`：正式行业分类与供应商概念标签分离。
9. `macro_rates`：宏观、央行、利率、收益率曲线。
10. `derivatives`：期货、期权链、OI、IV、Greeks、期限结构、skew。
11. `news_research`：新闻/研报元数据；正文访问受来源条款控制。
12. `sentiment_editorial`：热度、概念命中、编辑标签，必须标注非硬事实。

## 7. 字段级 Source Routing

禁止定义一个全局的“最佳网站”。路由以“市场 + 字段 + 时效要求 + 合规要求”为单位。

每个 source 注册：

```yaml
source_id: sec_edgar
authority: A
reliability: A
freshness: A
compliance: A
auth: declared_user_agent
rate_limit: 8_per_second
coverage:
  - us_filings
  - us_xbrl
known_issues: []
status: healthy
last_verified: 2026-08-15
```

路由评分至少考虑：

- Authority：权威程度。
- Reliability：技术稳定性。
- Freshness：时效性。
- Compliance：许可/使用风险。
- Coverage：字段覆盖度。
- Latency：响应速度。
- Rate-limit / IP-ban 风险。

默认原则：官方原始源 > 交易所/监管机构 > 稳定专业源 > 门户聚合源 > 媒体/二次转述。

但最终优先级必须字段级定义。例如 SEC XBRL 优先用于美股财报，而 CBOE 仅用于适合的期权字段。

## 8. Source Health 与降级

每个数据源维护状态：

- `healthy`
- `degraded`
- `broken`
- `deprecated`
- `blocked`

并记录：

```yaml
last_verified:
last_success:
last_failure:
failure_reason:
replacement:
```

Fallback 必须优先跨域名、跨限流平面。例如 Eastmoney 失败后优先切换 Sina / Tencent / SSE / SZSE，而不是切换另一个 Eastmoney endpoint 伪装成备用源。

禁止无限重试。建议默认：短超时 + 有限指数退避 + 失败后切换独立备用源。

## 9. 校验规则

按数据风险分级：

### Tier 1：高权威简单事实

例如官方宏观数据、官方财报、交易所公告。单一高权威源可通过，但仍保留 provenance。

### Tier 2：供应商衍生/口径差异数据

例如估值、行业分类、资金流、持仓。重要使用场景建议双源或官方源复核。

### Tier 3：异常值或重大结论依赖数据

必须双源验证或回到官方原始数据。

出现明显冲突时返回 `SOURCE_CONFLICT`，不得静默选择“看起来合理”的值。冲突记录应包含两个源的值、时间、单位、口径和可能原因。

基本质量检查包括：

- 时间戳/交易日一致性。
- 单位和币种一致性。
- 复权口径一致性。
- 数值类型与范围。
- OHLC 关系。
- 成交量/成交额非负。
- 时间序列排序与重复值。
- 缺失值比例。
- 跨源容差比较。

## 10. 本地派生计算

能确定性计算的指标尽量由本地统一实现，不依赖第三方技术指标 API。

首批包括：

- Return
- MA / EMA
- MACD
- RSI
- KDJ
- Bollinger
- Volatility
- Drawdown
- Turnover Rate（在自由流通股本可得且口径明确时）
- Historical Percentile
- Market Breadth
- Turnover Concentration

派生字段必须记录 `derived_from`、算法版本和参数。

## 11. 输出压缩与 Token 控制

所有适配器先产出标准化结构，再根据场景裁剪，禁止把巨型原始 JSON 直接送给 LLM。

支持三档：

- `compact`：只返回完成当前任务所需字段。
- `standard`：默认研究输出。
- `full`：调试/审计/完整数据。

原始响应仅在调试或显式请求时保留/展示。

## 12. 高阶工作流

financial-data 可以提供数据编排，但不能替上层研究 Skill 做最终投资判断。

首批 workflow：

- `single_stock_snapshot`
- `peer_comparison`
- `sector_rotation_dataset`
- `market_breadth_snapshot`
- `macro_snapshot`
- `event_dataset`
- `cross_section_fundamentals`

职责边界：workflow 负责“准备可靠、统一、可追溯的数据集”；买卖结论、主题判断、估值观点属于上层研究逻辑。

## 13. V1 数据源范围

优先实现稳定且覆盖关键场景的最小集合，不追求一开始复制全部 70+ endpoint。

### 中国市场

优先候选：

- Tencent：A 股/指数/ETF 基础行情、估值等。
- Sina：行情/财务/备用资金类数据。
- Eastmoney：独占/高价值数据，统一节流，避免作为所有数据的默认源。
- CNINFO：公告。
- SSE/SZSE：适用的官方数据/公告/龙虎榜备用。

`mootdx` 可作为增强适配器，但核心 Skill 不应强依赖重型第三方库。

### 美国/全球

优先候选：

- SEC EDGAR：filings/XBRL/CIK。
- US Treasury：收益率曲线。
- CFTC：COT。
- Yahoo：行情/期权备用，明确合规限制。
- CBOE/FINRA：先进入 registry 和 references；执行适配器是否默认启用由合规条款决定。

### V1 暂不强制完整实现

- 全量 0DTE unusual flow。
- 全量 A 股涨停生态全部 endpoint。
- 全文研报抓取。
- 舆情/社区抓取。
- 需要明显规避网站访问限制的 scraper。

这些保留接口和规范扩展位，但不牺牲首版稳定性。

## 14. 合规

来源 registry 必须记录：

- 是否允许程序访问。
- 是否允许商业使用。
- 是否允许再分发。
- 是否要求 API key / User-Agent / license。
- 条款最后核验日期。

“官方”不等于“可自由商业使用”。

禁止通过绕过验证码、访问控制、robots/明确条款限制等方式实现数据抓取。

## 15. 错误模型

统一错误码：

- `INSTRUMENT_NOT_FOUND`
- `FIELD_NOT_SUPPORTED`
- `SOURCE_UNAVAILABLE`
- `SOURCE_BLOCKED`
- `AUTH_REQUIRED`
- `RATE_LIMITED`
- `STALE_DATA`
- `NORMALIZATION_ERROR`
- `VALIDATION_FAILED`
- `SOURCE_CONFLICT`
- `COMPLIANCE_RESTRICTED`

错误必须包含可解释的 fallback 结果，禁止静默返回空数组冒充成功。

## 16. 测试与验收

### 单元测试

- 标的代码规范化和 alias 映射。
- 单位/百分比/币种标准化。
- 数据契约必填字段。
- 路由排序和 fallback。
- 跨源冲突判断。
- 技术指标的确定性结果。

### Fixture 测试

使用固定响应样本测试解析，不依赖实时网络，防止上游短期波动导致测试不稳定。

### Live smoke test

少量可选在线检查：

- 一个 A 股行情标的。
- 一个美股 SEC 标的。
- Treasury yield curve。

网络测试失败不能自动判定全部代码错误，应区分网络/上游变化和解析错误。

### 仓库级验收

- `python3 scripts/validate_skills.py` 通过。
- `skills/financial-data/SKILL.md` frontmatter 名称与目录一致。
- 所有核心 Python 单元测试通过。
- 不把密钥、Cookie、个人 SEC 联系信息硬编码进仓库。

## 17. README 与 Agent 体验

README 需要提供少量直接自然语言示例：

- “获取贵州茅台过去 250 个交易日日线并计算 20/60/120 日均线。”
- “比较宁德时代、比亚迪、亿纬锂能最新估值与盈利增速。”
- “获取 AAPL 最新 10-Q 的收入、净利润和经营现金流，附来源。”
- “获取美债 2Y/10Y 并计算期限利差。”
- “构建昨日 A 股申万行业涨跌和成交占比数据集。”

Agent 默认只加载当前任务需要的 reference，不一次性吞入全部市场文档。

## 18. 版本策略

建议初始版本 `0.1.0`。

- patch：修复 endpoint、解析、映射、文档。
- minor：增加新的数据源/数据类别/工作流。
- major：破坏数据契约或核心调用接口。

Source registry 的接口状态变化不强制提升 Skill major version，但必须记录 `last_verified` 和变更说明。

## 19. 成功标准

首版完成后，应满足：

1. 一个 Agent 不需要记住底层网站参数即可请求常见 A 股/美股/宏观数据。
2. 同一种字段跨源输出统一 schema、单位和时间语义。
3. 主源失败可明确降级，不静默失真。
4. 每个关键数据可追踪到来源与抓取时间。
5. 可确定性派生指标由本地统一计算。
6. Skill 主文件保持轻量，新增数据源无需重写整体架构。
7. 能直接作为晨报、A 股看板、研究脚本、回测数据准备的底层公共能力。

## 20. 非目标

financial-data 不负责：

- 给出最终投资建议。
- 自动替用户交易。
- 建立大型持久化行情数据库。
- 替代付费专业数据终端。
- 为追求覆盖率而绕过数据源的访问限制。

其核心价值是：让上层 Agent 使用金融数据时拥有统一、可复现、可审计的数据基础层。
