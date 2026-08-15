# 美股/港股/全球股票行情数据手册

## 目标能力

- US/HK quote、K线（日/周/月/分钟）、指数/ETF。
- 全市场股票列表、涨跌/成交排名。
- 证券搜索：中英文名称、ticker、交易所映射。
- 新闻/事件元数据。

## 推荐公共研究路由

| 数据 | 首选/候选 | 说明 |
|---|---|---|
| US quote | Sina / Tencent / Eastmoney | 研究便利源；生产用途核对许可 |
| HK quote | Tencent | 字段较全；Eastmoney/Sina fallback |
| US K-line | Sina / Yahoo chart | Yahoo 支持多周期；cookie/网络需处理 |
| HK K-line | Yahoo chart | 需核对当前可达性/条款 |
| 全市场列表 | Eastmoney clist | US/HK 横截面、排名 |
| 搜索 | Eastmoney search / Yahoo search / official mappings | 结果必须回到 Instrument Master |

## Yahoo chart

典型 endpoint family: `query1.finance.yahoo.com/v8/finance/chart/<symbol>`。项目应记录 `regularMarketTime`/bar timezone、adjclose 与 raw close、dividend/split、interval 回溯限制以及 cookie/crumb 是否为具体 endpoint 所需。内部 canonical symbol 与 Yahoo alias 分开存。

## Sina/Tencent US-HK quote

适合大陆网络环境研究 fallback。不同市场字段索引不应共用 parser；每个 provider/market 单独 fixture。中文名称、PE/EPS 等 vendor fields 保存 `raw_field` + `methodology_id`。

## 全市场列表/搜索

Eastmoney `push2/clist` 和 search family 可用于 NASDAQ/NYSE/HK 横截面、涨跌/成交排序和中英文证券发现。`secid` 只做 provider alias，不做长期主键。

## Market data contract

K线统一 timestamp、trade_date、OHLC、volume、currency、adjustment、source；成交量单位显式声明。
