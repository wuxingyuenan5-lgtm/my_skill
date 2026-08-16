# Futures Source Recipes

## 中国期货官方层

六家境内期货交易所的**日级真实合约行情/结算**已经进入 READY Core。统一入口、字段合同、机器请求 family、单位和错误语义见 [`futures-ready-core.md`](futures-ready-core.md)。

```python
from financial_data import fetch_cn_futures_daily

rows = fetch_cn_futures_daily("GFEX", "2026-08-14")
```

| Exchange | 日行情/结算 | 会员成交/持仓排名 | 其他重点数据 |
|---|---|---|---|
| SHFE | **READY** | **READY** | 仓单日报、库存周报、结算/交易参数 |
| INE | **READY** | **RECIPE / parser-ready** | 仓单/库存、结算/交易参数 |
| DCE | **READY** | **READY** | 仓单、交割、业务参数 |
| CZCE | **READY（现代 2016+）** | **READY（当前 XLSX regime）** | 仓单/交割、规则参数 |
| CFFEX | **READY** | **READY** | 结算参数、历史数据、交易参数 |
| GFEX | **READY** | **READY** | 仓单、交割、业务参数 |

会员排名的统一接口和长表事实合同见 [`futures-positioning-ready-core.md`](futures-positioning-ready-core.md)。当前 umbrella `cn_futures_member_positions` 仍保持 RECIPE，因为 INE 的官方 Daily Ranking 页面虽已确认，但机器 fetch path 尚未冻结；不得把 5/6 READY 虚报为 6/6 READY。

```python
from financial_data import fetch_cn_futures_positions

positions = fetch_cn_futures_positions("SHFE", "2026-08-14")
```

READY 只代表仓库存在可复用 fetch/parser 和确定性测试，不代表交易所网页/API 永久不变。项目仍应冻结 parser fixture、`source_url`、raw payload/file hash 和项目自己的 `last_verified`。

`close`、`settlement`、`pre_settlement` 必须分开保存；跨交易所使用 `turnover` 前先检查 `turnover_unit`。当前 CFFEX 与明确写出“万元”的 CZCE 表头使用 `CNY_10K`，其他交易所统一层暂保守记录 `provider_declared`。

会员排名也有独立语义：成交排名、持多排名、持空排名是三张独立榜单；Top-N long-minus-short 是披露子集的派生量，不是全市场净持仓。集中度必须提供同合约、同交易日的 total volume / open interest 分母。

## 下一批 READY 化

完成日行情和大部分会员排名后，推荐顺序调整为：

1. **仓单/库存**：仓单日报、库存周报、交割库存；
2. **交易参数**：保证金、涨跌停、手续费、交割规则；
3. **INE positioning transport**：若当前 WAF/机器下载路径能稳定冻结，则补齐 umbrella 6/6 READY；
4. **CTP/授权实时行情**：TradingDay/ActionDay/UpdateTime、盘口、逐笔与分钟构建。

## 国内实时/分钟行情层

优先级：机构自有/期货公司 CTP（生产） > licensed vendor > 公共网页/开源 adapter（研究/原型）。CTP 项目保存 TradingDay、ActionDay、UpdateTime/Millisec、InstrumentID、LastPrice、Volume、Turnover、OpenInterest、Bid/Ask。夜盘不能只用本机 calendar date 判断交易日。

## 海外期货

- CME/CBOT/NYMEX/COMEX：股指、利率、能源、金属、农产品；实时/历史通常涉及 entitlement。
- ICE：能源、软商品、利率等，数据许可单独评估。
- LME：基本金属期限结构口径特殊；跨 LME/COMEX/SHFE 比价统一 currency/unit/tax/location/time。
- SGX：亚洲指数/铁矿等；与国内品种比较先建 contract-spec bridge。

AkShare/Tushare/社区 wrapper 适合 discovery/原型，但 provenance 最终记录底层 source，而不是 wrapper 名。