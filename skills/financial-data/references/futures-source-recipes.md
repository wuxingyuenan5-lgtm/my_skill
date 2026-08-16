# Futures Source Recipes

## 中国期货官方层

六家境内期货交易所的**日级真实合约行情/结算**已经进入 READY Core。统一入口、字段合同、机器请求 family、单位和错误语义见 [`futures-ready-core.md`](futures-ready-core.md)。

```python
from financial_data import fetch_cn_futures_daily

rows = fetch_cn_futures_daily("GFEX", "2026-08-14")
```

| Exchange | 日行情/结算 | 其他重点数据 | 建议用途 |
|---|---|---|---|
| SHFE | **READY** | 日交易排名、每日结算参数、仓单日报、库存周报、历史下载 | 沪铜/金银/螺纹等 |
| INE | **READY** | 排名、结算参数、仓单/库存、交割 | 原油/低硫/国际铜等 |
| DCE | **READY** | 成交持仓、仓单、交割、业务参数 | 铁矿/焦煤焦炭/农产品/化工 |
| CZCE | **READY（现代 2016+ 路径）** | 持仓排名、仓单/交割、规则参数 | 棉花/白糖/PTA/甲醇等 |
| CFFEX | **READY** | 成交持仓排名、结算参数、历史数据 | IF/IH/IC/IM、国债期货 |
| GFEX | **READY** | 仓单、成交持仓排名、交割与业务参数 | 工业硅/碳酸锂等 |

READY 只代表仓库存在可复用 fetch/parser 和确定性测试，不代表交易所网页/API 永久不变。项目仍应冻结 parser fixture、`source_url` 和项目自己的 `last_verified`。

`close`、`settlement`、`pre_settlement` 必须分开保存；跨交易所使用 `turnover` 前先检查 `turnover_unit`。当前 CFFEX 与明确写出“万元”的 CZCE 表头使用 `CNY_10K`，其他交易所统一层暂保守记录 `provider_declared`。

## 下一批 READY 化

日行情之后按以下顺序继续：

1. **会员成交/持仓排名**：多空席位、成交量排名、集中度；
2. **仓单/库存**：仓单日报、库存周报、交割库存；
3. **交易参数**：保证金、涨跌停、手续费、交割规则；
4. **CTP/授权实时行情**：TradingDay/ActionDay/UpdateTime、盘口、逐笔与分钟构建。

这些数据仍分别参考 `futures-positioning-warehouse.md`、`futures-trading-parameters.md` 与本页实时行情章节，不因日行情 READY 而自动视为 READY。

## 国内实时/分钟行情层

优先级：机构自有/期货公司 CTP（生产） > licensed vendor > 公共网页/开源 adapter（研究/原型）。CTP 项目保存 TradingDay、ActionDay、UpdateTime/Millisec、InstrumentID、LastPrice、Volume、Turnover、OpenInterest、Bid/Ask。夜盘不能只用本机 calendar date 判断交易日。

## 海外期货

- CME/CBOT/NYMEX/COMEX：股指、利率、能源、金属、农产品；实时/历史通常涉及 entitlement。
- ICE：能源、软商品、利率等，数据许可单独评估。
- LME：基本金属期限结构口径特殊；跨 LME/COMEX/SHFE 比价统一 currency/unit/tax/location/time。
- SGX：亚洲指数/铁矿等；与国内品种比较先建 contract-spec bridge。

AkShare/Tushare/社区 wrapper 适合 discovery/原型，但 provenance 最终记录底层 source，而不是 wrapper 名。