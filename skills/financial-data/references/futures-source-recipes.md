# Futures Source Recipes

## 中国期货官方层

| Exchange | 重点数据 | 建议用途 |
|---|---|---|
| SHFE | 日交易快讯/排名、每日结算参数、仓单日报、库存周报、历史下载 | 沪铜/金银/螺纹等定义与结算 |
| INE | 原油/低硫/国际铜等行情、结算、交割/仓单 | 国际化能源品种 |
| DCE | 日行情、成交持仓、仓单、交割、业务参数 | 铁矿/焦煤焦炭/农产品/化工 |
| CZCE | 日行情、持仓排名、仓单/交割、规则参数 | 棉花/白糖/PTA/甲醇等 |
| CFFEX | 日统计、成交持仓排名、结算参数、历史数据 | IF/IH/IC/IM、国债期货 |
| GFEX | 工业硅/碳酸锂等行情、持仓、交割与业务参数 | 新能源商品 |

官方网页 endpoint 会改版。Recipe 应记录入口页面、实际请求 path、parser fixture、`last_verified`。

SHFE 官方统计入口 `https://www.shfe.com.cn/reports/tradedata/dailyandweeklydata/` 当前包含日交易快讯、日交易排名、每日结算参数、仓单日报、每周行情、库存周报等，适合作为定义/结算/仓单事实层。

## 国内实时/分钟行情层

优先级：机构自有/期货公司 CTP（生产） > licensed vendor > 公共网页/开源 adapter（研究/原型）。CTP 项目保存 TradingDay、ActionDay、UpdateTime/Millisec、InstrumentID、LastPrice、Volume、Turnover、OpenInterest、Bid/Ask。夜盘不能只用本机 calendar date 判断交易日。

## 海外期货

- CME/CBOT/NYMEX/COMEX：股指、利率、能源、金属、农产品；实时/历史通常涉及 entitlement。
- ICE：能源、软商品、利率等，数据许可单独评估。
- LME：基本金属期限结构口径特殊；跨 LME/COMEX/SHFE 比价统一 currency/unit/tax/location/time。
- SGX：亚洲指数/铁矿等；与国内品种比较先建 contract-spec bridge。

AkShare/Tushare/社区 wrapper 适合 discovery/原型，但 provenance 最终记录它的底层 source，而不是 wrapper 名。
