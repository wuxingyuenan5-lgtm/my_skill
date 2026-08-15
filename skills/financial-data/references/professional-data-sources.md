# Professional and Licensed Data Sources

这个 Skill 不只收录免费 API。当项目从原型进入生产，最合适的来源可能是付费/授权数据。

## China institutional terminals

- Wind：A/H/全球股票、期货、基金、宏观、行业、财务、估值、公告、交易日、衍生品。Wind code 放 Instrument Master alias，API/终端授权标 `RESTRICTED`。
- Choice：覆盖中国金融市场与研究数据；账号/终端授权不写入公共仓库。
- Tushare Pro：适合有 token 的 Python 项目，股票/指数/期货/基金/宏观结构化数据；token 只放环境变量，权限/再分发按当前条款。

## Global institutional sources

Bloomberg、LSEG/Refinitiv 适合全球行情、参考数据、公司行为、估值、衍生品和新闻；BBGID/RIC 等作为 alias，不取代 canonical ID。

## Broker / exchange licensed feeds

国内期货 CTP、股票/期权券商 L1/L2、CME/ICE/LME entitlement/vendor feed。TradingView 图表库许可与市场数据许可是两件事。

## Crypto exchanges

Binance/Coinbase/OKX 等可作为 crypto 第一方行情/订单簿/衍生品源；rate limit、地区/账户权限、symbol/contract type 单独建 registry。

## Prototype -> production

```text
Public web prototype
 -> validate field semantics
 -> freeze canonical schema
 -> add licensed source adapter
 -> dual-run comparison
 -> switch production primary
 -> retain public research fallback if terms allow
```

不要让上层依赖免费网页原始字段名；统一 schema 才能低成本迁移。
