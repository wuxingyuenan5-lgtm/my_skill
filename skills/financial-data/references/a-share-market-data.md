# A股行情与时间序列数据手册

## 能力范围

- 实时/延时 quote：价格、昨收、开高低、涨跌幅、成交量/额、换手率、PE/PB、市值、涨跌停价、量比。
- K线：1m/5m/15m/30m/60m/日/周/月等，区分不复权、前复权、后复权。
- 五档盘口、逐笔成交。
- 指数、ETF、北交所证券。
- 全市场列表、横截面行情、市场宽度基础数据。

## READY 能力

### Tencent A股 K-line

共享 runtime 已支持：

```python
from financial_data import DataRequest, get_data

r = get_data(DataRequest(
    "600519.SH",
    "kline",
    params={"resolution": "1d", "adjustment": "qfq", "count": 250},
))
```

支持 resolution：`1m`、`5m`、`15m`、`30m`、`60m`/`1h`、`1d`、`1w`、`1mo`。日/周/月支持 `qfq`、`hfq`、`none`；分钟线统一按 `none` 处理。

每根 K 线返回一个 `DataPoint(field="bar")`，`value` 中保存 `open/high/low/close/volume`。Facade 会对整个 bar 执行 OHLCV 合法性校验。

分钟端点的额外 provider 字段**不自动解释为成交额**，统一保存到 `metadata.provider_extra_fields`。参考仓库曾确认部分分钟 K 线第 7 字段属于换手相关数据而非成交额；除非再次验证口径，否则不要重命名成 `turnover`。

当前共享 helper 将 volume 标记为 `provider_native`。如果项目需要严格的 shares/lots 口径，应在项目提取阶段用交易所/供应商定义进一步冻结。

## 推荐路由

| 数据 | 首选 | 备选 | 说明 |
|---|---|---|---|
| A股 quote/估值/市值/换手 | Tencent | Sina / Eastmoney | Tencent 字段丰富；商业使用需核对条款 |
| 日/分钟 K线 | **Tencent READY** / mootdx | Sina / Baidu | Tencent HTTP 方便；mootdx 适合原始价与本地研究 |
| 五档/逐笔 | mootdx | 券商/授权行情 | 生产系统优先 licensed feed |
| 指数/ETF quote | Tencent | Eastmoney/Sina | 必须显式解决 `000001`、`000300` 等市场歧义 |
| 全市场横截面 | Eastmoney Push2 | licensed vendor | 共享 EastmoneyClient 可复用，但完整 A股含 BSE 覆盖仍按项目 recipe 冻结 |

## Tencent quote recipe

Endpoint family: `https://qt.gtimg.cn/q=<symbols>`，GBK，`~` 分隔。

已校准的重要索引：3 当前价；4 昨收；5 今开；31 涨跌额；32 涨跌幅百分数；33/34 高/低；37 成交额源单位“万元”；38 换手率百分数；39 PE(TTM)；43 振幅百分数；44 流通市值亿元；45 总市值亿元；46 PB；47/48 涨停/跌停；49 量比；52 静态 PE。

标准化：成交额乘 `10_000` 为 CNY；百分数字段除 `100` 变 decimal；亿元乘 `1e8`。

### 代码/市场前缀

- 6 开头股票通常 `sh`；0/2/3 通常 `sz`；920 新号段为 `bj`。
- 5 开头 ETF 属沪市；沪市指数需要白名单/显式前缀。
- `000001` 不可裸猜：`sh000001`=上证指数，`sz000001`=平安银行。
- 北交所旧 43/83/87 号段大量已迁到 920xxx。HTTP 200 不代表当前代码有效；零成交且价格定格时要判 `stale`，最好按证券名称/交易所清单反查现行代码。

## Tencent K-line source families

- 日/周/月复权：`web.ifzq.gtimg.cn/appstock/app/fqkline/get`
- 分钟：`ifzq.gtimg.cn/appstock/app/kline/mkline`

项目冻结时记录 resolution 映射、复权模式、bar 字段顺序、成交量单位和附加字段含义。大规模循环也应节流；参考仓库曾观察到高频连续请求后返回空，不能把空结果直接解释为“没有历史行情”。

## mootdx recipe

协议：通达信 TCP 7709。能力：K线、46字段 quote、五档、逐笔、财务快照、F10。

关键坑点：`bars()` 使用 `frequency`；错误传 `category` 可能被静默吞掉；bars 为原始不复权价格；某些 mootdx 版本 `BESTIP.HQ` 空字符串会触发连接异常。项目应维护候选服务器并以“真实拉到一根 bar”验活，而不是只做 TCP 握手。

## Baidu K-line

可作为低频 fallback；部分接口直接返回 MA5/10/20。需要回测一致性时仍应从标准化 OHLCV 本地重算指标。

## 全市场列表

`financial_data.eastmoney.EastmoneyClient` 已提供通用 Push2 market-list helper；但 `cn_market_cross_section` 当前仍保持 `RECIPE`，因为完整 A股横截面需要项目明确冻结上交所、深交所、北交所范围和 provider `fs` 组合，不能把不完整 universe 冒充“全A”。

## 标准输出建议

```yaml
instrument_id: equity_cn_600519
symbol: 600519.SH
trade_date: 2026-08-14
as_of: 2026-08-14T15:00:00+08:00
open: 0
high: 0
low: 0
close: 0
volume: 0
volume_unit: provider_native
adjustment: qfq | hfq | none
source_id: tencent
retrieved_at: ...
```
