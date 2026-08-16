# 美股/港股/全球股票行情数据手册

## 目标能力

- US/HK quote、K线（日/周/月/分钟）、指数/ETF。
- 全市场股票列表、涨跌/成交排名。
- 证券搜索：中英文名称、ticker、交易所映射。
- 新闻/事件元数据。

## READY 能力

### Yahoo v8 Chart：US/HK K-line

```python
from financial_data import DataRequest, get_data

us = get_data(DataRequest("AAPL.US", "kline", params={"interval": "1d", "range": "1y"}))
hk = get_data(DataRequest("0700.HK", "kline", params={"interval": "1h", "range": "1mo"}))
```

共享 adapter 使用 `query2.finance.yahoo.com/v8/finance/chart/<symbol>`。US alias 为 `AAPL`；HK 保留 `0700.HK`。支持 `1m/2m/5m/15m/30m/60m/1h/1d/1w/1wk/1mo/3mo`；具体历史回溯长度仍受 Yahoo endpoint 当前规则限制。

Parser 会：

- 显式冒泡 `chart.error`；
- 跳过 OHLC 为 null 的空 bar；
- 保留 `exchangeTimezoneName`；
- `as_of` 使用 UTC timestamp；`trade_date` 根据交易所时区计算；
- `adjclose` 存到 bar value 的 `adj_close`，不偷换原始 close；
- 不把 v8 chart 描述成授权生产行情。Yahoo 仍按 research-only/当前条款处理。

如果传 `start/end`，adapter 使用 `period1/period2`；否则使用 `range`。长期项目需冻结 interval 的最大可回溯范围和 corporate-action 处理方式。

### Eastmoney 全市场列表 / 证券搜索

```python
from financial_data import EastmoneyClient

em = EastmoneyClient(min_interval=1.0)
leaders = em.market_stock_list("us_nasdaq", sort_field="f3", page_size=50)
hits = em.search_securities("腾讯")
```

当前内置市场 alias：`us_nasdaq`、`us_nyse`、`us_etf`、`hk`，并提供 `cn_a` 作为研究 helper。返回结果会标准化价格/涨跌幅/振幅等常用字段，并保留 `raw` provider row。

`search_securities()` 默认只返回 105/106/107/116（NASDAQ/NYSE/US ETF/HK）结果；搜索得到的 provider code 仍必须进入 Instrument Master，不能直接作为长期 canonical ID。

## 推荐公共研究路由

| 数据 | 首选/候选 | 说明 |
|---|---|---|
| US quote | Sina / Tencent / Eastmoney | 研究便利源；生产用途核对许可 |
| HK quote | Tencent | 字段较全；Eastmoney/Sina fallback |
| US/HK K-line | **Yahoo v8 Chart READY** | 共享 adapter；保留时区/null/error/adjclose 语义 |
| 全市场列表 | **EastmoneyClient READY** | US/HK 横截面、排名；严格 throttle |
| 搜索 | **EastmoneyClient READY** / Yahoo / official mappings | 结果必须回到 Instrument Master |

## Yahoo endpoint notes

Chart endpoint 不需要把 cookie/crumb 当作统一前提；Yahoo 的 quoteSummary/options 等其他 family 可能需要 cookie/crumb。Registry 因此标记为 `mixed_none_or_cookie_crumb`，避免用一个认证结论覆盖所有 Yahoo endpoint。

## Sina/Tencent US-HK quote

适合大陆网络环境研究 fallback。不同市场字段索引不应共用 parser；每个 provider/market 单独 fixture。中文名称、PE/EPS 等 vendor fields 保存 `raw_field` + `methodology_id`。

## Market data contract

K线统一 timestamp、trade_date、OHLC、volume、currency、adjustment、source；成交量单位显式声明。供应商搜索/全市场列表保留 provider raw 字段，以便字段变化时可追溯。
