# 美股基本面 / SEC 研究

## Objective
用上市公司官方披露和 SEC XBRL 支持财务、公告、事件和历史 point-in-time 研究。

## Required datasets
- `../datasets/global-equity/sec-filings-companyfacts.md`
- 价格对齐时：`../datasets/global-equity/kline.md`

## Optional datasets
分析师一致预期、机构持仓、估值供应商字段：见 `../references/global-equity-fundamentals.md`，通常是 vendor-derived 或授权数据。

## Recommended source path
事实披露优先 `../providers/sec-edgar.md`；价格可 shortlist Yahoo 或授权供应商。

## Methodology / caveats
区分 fiscal period、filing date、accepted/published/available date；10-K/10-Q修订与XBRL历史值可能更新。回测必须用当时可获得信息而不是最新 companyfacts 快照倒灌。

## What to freeze into the downstream project
CIK/ticker映射、SEC User-Agent、filing/companyfacts recipe、PIT日期、XBRL字段映射、缓存和last_verified。

## Avoid unnecessary reads
无需读取A股、期货、Crypto或所有美股vendor文档。