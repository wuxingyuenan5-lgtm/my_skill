# A股资金、筹码与持仓结构数据

## 数据集

个股分钟/日资金流、融资融券、龙虎榜席位、大宗交易、股东户数、限售解禁、分红送转、行业/概念/地域资金流、互联互通数据。

## Eastmoney datacenter 统一模式

龙虎榜、解禁、两融、大宗、股东、分红等多个数据集来自 `datacenter-web.eastmoney.com/api/data/v1/get` 的不同 `reportName`。建议项目实现统一 helper：

```python
def eastmoney_datacenter(session, report_name, columns='ALL', filter_str='', page_size=50,
                         sort_columns='', sort_types='-1'):
    params = {'reportName': report_name, 'columns': columns, 'filter': filter_str,
              'pageNumber': '1', 'pageSize': str(page_size), 'sortColumns': sort_columns,
              'sortTypes': sort_types, 'source': 'WEB', 'client': 'WEB'}
    r = session.get('https://datacenter-web.eastmoney.com/api/data/v1/get', params=params, timeout=15)
    r.raise_for_status()
    return ((r.json().get('result') or {}).get('data')) or []
```

不要把 `[]` 自动解释成“没有事件”；HTTP/业务异常、字段变更、风控和真实无记录必须区分。

## Provider throttle

统一 session + 串行最小间隔 + jitter；429/5xx 退避；403 视为风控而非持续重试；不同 Eastmoney 子域维护独立 health state。批量任务优先先拉横截面再本地过滤，避免逐股 N×endpoint。

## 数据语义

- 龙虎榜：trade_date、reason、buy/sell/net amount、seat/broker、institution flag。长期无上榜是正常空集。
- 解禁：unlock_date、type、free_shares、actually_floatable_shares、占总/流通比例；保留 raw field map version。
- 两融：融资余额/买入/偿还、融券余额/余量/卖出；属于收盘后数据，不等于盘中资金流。
- 大宗：价格、量/额、相对收盘溢折价、买卖方营业部；溢折价标准化为 decimal。
- 股东户数：统计截止日和披露日分离，回测按 `available_at`。
- 资金流：主力/超大/大/中/小单是 vendor order-size classification，不是官方投资者身份；保存 `methodology_id`。
- 北向/互联互通：披露制度变化后部分分钟序列可能不再可靠；权威日统计优先交易所/港交所或 licensed vendor，不绕过反爬条款。
