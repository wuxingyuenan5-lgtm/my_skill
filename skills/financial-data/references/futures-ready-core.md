# 中国期货官方日行情 READY Core

## 定位

本页对应 `financial_data.cn_futures_official`。它不是行情供应商聚合器，而是六家境内期货交易所官方日行情/结算数据的可复用解析与抓取层。

公共入口：

```python
from financial_data import fetch_cn_futures_daily

rows = fetch_cn_futures_daily("SHFE", "2026-08-14")
```

也可以直接调用交易所函数：

```python
from financial_data.cn_futures_official import (
    fetch_shfe_daily,
    fetch_ine_daily,
    fetch_dce_daily,
    fetch_czce_daily,
    fetch_cffex_daily,
    fetch_gfex_daily,
)
```

## Canonical daily row

所有交易所都归一为同一结构：

```yaml
contract_id: CU2609
variety: CU
exchange: SHFE
trade_date: 2026-08-14
delivery_month: '2609'
open: 0
high: 0
low: 0
close: 0
settlement: 0
pre_settlement: 0
volume: 0
turnover: 0
open_interest: 0
currency: CNY
volume_unit: contracts
turnover_unit: provider_declared
source_id: shfe
source_url: ...
raw: {...}
```

硬规则：

- `close`、`settlement`、`pre_settlement` 是三个独立字段，不允许互相补值。
- `contract_id` 是真实交易合约，不是“主力/连续”虚拟代码。
- `delivery_month` 必须从交易所字段或合约代码显式得到，供期限结构使用。
- `volume`、`open_interest`、`turnover` 不得为负。
- OHLC 完整时必须满足高低价一致性。
- `小计/合计/总计` 等汇总行在 provider parser 层剔除。
- HTTP 成功但业务 payload 异常不会被解释成“空数据成功”。

## 六家交易所

### SHFE

函数：`fetch_shfe_daily()` / `parse_shfe_daily_payload()`。

机器数据 family：

```text
https://www.shfe.com.cn/data/tradedata/future/dailydata/kxYYYYMMDD.dat
```

解析 `o_curinstrument`，核心字段包括 `OPENPRICE`、`HIGHESTPRICE`、`LOWESTPRICE`、`CLOSEPRICE`、`SETTLEMENTPRICE`、`PRESETTLEMENTPRICE`、`VOLUME`、`OPENINTEREST`、`TURNOVER`。

### INE

函数：`fetch_ine_daily()` / `parse_ine_daily_payload()`。

机器数据 family：

```text
https://www.ine.cn/data/tradedata/future/dailydata/kxYYYYMMDD.dat
```

结构与 SHFE 相近，但 source/exchange/provenance 独立保存；不能因为 schema 相似就把两者当同一个源。

### DCE

函数：`fetch_dce_daily()` / `parse_dce_daily_payload()`。

当前日统计请求 family：

```text
https://www.dce.com.cn/dcereport/publicweb/dailystat/dayQuotes
```

POST 参数包含 `tradeDate`、`tradeType=1`、`varietyId=all` 等。核心 provider 字段：`contractId/open/high/low/close/lastClear/clearPrice/volumn/openInterest/turnover`。

### CZCE

函数：`fetch_czce_daily()` / `parse_czce_daily_text()`。

READY fetcher 当前明确支持现代 `DFSStaticFiles` regime（2016 年及以后）：

```text
https://www.czce.com.cn/cn/DFSStaticFiles/Future/YYYY/YYYYMMDD/FutureDataDaily.txt
```

文本按交易所表头解析；常见字段含 `昨结算/今开盘/最高价/最低价/今收盘/今结算/成交量(手)/空盘量/成交额(万元)`。更早历史格式继续作为 RECIPE，不在 READY fetcher 内猜测路由。

### CFFEX

函数：`fetch_cffex_daily()` / `parse_cffex_history_zip()` / `parse_cffex_daily_csv()`。

历史月包 family：

```text
https://www.cffex.com.cn/sj/historysj/YYYYMM/zip/YYYYMM.zip
```

包内读取 `YYYYMMDD_1.csv`。默认 parser 保留期权合约；需要纯期货时显式 `futures_only=True`。成交额按交易所日统计口径保存为 `turnover_unit=CNY_10K`，不与其他交易所未经验证的成交额单位混用。

### GFEX

函数：`fetch_gfex_daily()` / `parse_gfex_daily_payload()`。

当前日行情请求 family：

```text
https://www.gfex.com.cn/u/interfacesWebTiDayQuotes/loadList
```

核心 provider 字段：`varietyOrder/delivMonth/open/high/low/close/lastClear/clearPrice/volumn/openInterest/turnover`。

## 与已有期货工具衔接

标准行可以直接输入：

```python
from financial_data.futures import select_dominant_contract, term_structure

rows = fetch_cn_futures_daily("SHFE", "2026-08-14")
cu = [row for row in rows if row["variety"] == "CU"]

dominant = select_dominant_contract(cu, metric="open_interest")
curve = term_structure(cu, price_field="settlement")
```

这仍然只是在一组真实合约中执行“主力选择”和“期限结构排序”；不会把主力合约或连续合约伪装成真实可交易合约。

## Turnover unit

当前实现采用保守原则：

- CFFEX：`CNY_10K`。
- CZCE：当表头明确为 `成交额(万元)` 时为 `CNY_10K`。
- SHFE / INE / DCE / GFEX：在统一模块中先保留 `provider_declared`，直到对应交易所当前字段定义和换算口径被独立冻结并加入测试。

因此，跨交易所比较成交额之前必须先完成单位转换；不要直接把 `turnover` 数值横向拼接。

## 错误语义

- HTTP 401/403/429/5xx 走共享 `HttpClient` 分类。
- JSON 缺少预期数组、CSV/文本表头无法识别、ZIP 中缺少目标日期文件：显式抛 `FinancialDataError`。
- CZCE 错误页不返回 `[]` 冒充无交易。
- 真正的非交易日/合法空数据，应由上层交易日历和业务策略决定如何表达；不要靠 provider error page 推断。

## 当前边界

本 READY Core 只覆盖**日级合约行情/结算**。以下仍分批建设：

1. 会员成交/持仓排名；
2. 仓单日报与库存；
3. 保证金、涨跌停、手续费与交割参数；
4. CTP/授权实时行情。

项目抽取时建议把本模块、对应测试 fixture、交易日历/session master 和 contract master 一起冻结到目标项目。