# 美股/港股基本面、估值与机构数据

## 三层来源

1. **SEC EDGAR**：美国上市公司法定 filings/XBRL，事实层优先。
2. **公司 IR / 交易所公告**：非美公司或补充材料。
3. **Yahoo/Eastmoney 等 vendor**：估值、分析师预期、目标价、机构持仓、中文字段便利层。

## SEC Company Facts

适合 Revenue、NetIncomeLoss、EPS、Assets、Liabilities、StockholdersEquity、OCF、R&D、回购、股息等。标签可能因公司而异，跨公司比较要处理等价 tags 和单位。PIT 回测使用 filing/accepted/available time，不只用 fiscal period end。

## Eastmoney US/HK statements

Datacenter/F10 family 可提供中文三表与关键指标。属于 provider normalization，保留会计准则、币种、REPORT_DATE、raw item code。

## Yahoo quoteSummary

常见模块：financialData、defaultKeyStatistics、summaryDetail、statements histories、earningsTrend、recommendationTrend、upgradeDowngradeHistory、institutionOwnership。可取 trailing/forward PE、PB、EV、EV/EBITDA、ROE、margin、analyst targets、recommendation、EPS forecast、institutional holders。

这些属于 vendor-derived/consensus，保存 `as_of`、`forecast_period`、`provider_module`。

## 估值快照标准

```yaml
price:
market_cap:
enterprise_value:
pe_ttm:
pe_forward:
pb:
ev_ebitda:
roe:
revenue_ttm:
eps_ttm:
eps_fy1:
target_mean:
source_map: {}
as_of:
```

法定财务和当前估值/一致预期可以来自不同层，不强求单一 source。
