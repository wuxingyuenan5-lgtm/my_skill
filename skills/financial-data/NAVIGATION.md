# financial-data Navigation

Use this file as the default first hop after `SKILL.md`.

**Progressive-disclosure rule:** do not scan the full Skill by default. Open one first-hop card, then only the shortlisted provider/reference files needed to answer the request. A normal narrow lookup should usually stay within **3-5 small files total**. Do not read `references/capability-index.yaml` in full unless the request is about global coverage, capability status, or maintenance/audit.

## 1. Research-task routes

| User intent | First hop |
|---|---|
| A股均线、技术策略、日K回测 | `tasks/a-share-ma-strategy.md` |
| A股市场宽度、成交额、百亿股、横截面 | `tasks/a-share-market-breadth.md` |
| 期货主力、期限结构、Contango/Backwardation、跨期 | `tasks/futures-term-structure.md` |
| 期货席位、会员持仓、Top5/10/20、多空集中度 | `tasks/futures-positioning.md` |
| 碳酸锂、LC、广期所碳酸锂研究 | `tasks/lithium-carbonate-research.md` |
| 铜、铜期货、铜产业/铜矿股联动 | `tasks/copper-research.md` |
| 跨资产研究、交易晨报、全球资产联动 | `tasks/cross-asset-research.md` |
| 美股基本面、SEC公告、财报/XBRL | `tasks/us-equity-fundamentals.md` |

## 2. Concrete-dataset routes

| Needed data | First hop |
|---|---|
| A股/中国股票 K线 | `datasets/cn-equity/kline.md` |
| A股全市场横截面/成交额/市值/涨跌 | `datasets/cn-equity/market-cross-section.md` |
| A股行业分类/申万等历史归属 | `datasets/cn-equity/industry-classification.md` |
| 国内期货真实合约日行情/结算/OI | `datasets/futures/daily-contract-market-data.md` |
| 国内期货会员成交/多空持仓排名 | `datasets/futures/member-position-ranking.md` |
| 期货仓单/库存 | `datasets/futures/warehouse-inventory.md` |
| 期货保证金/涨跌停/手续费/交易时段/交割参数 | `datasets/futures/trading-parameters.md` |
| 美股/港股 K线 | `datasets/global-equity/kline.md` |
| SEC filings / companyfacts | `datasets/global-equity/sec-filings-companyfacts.md` |
| 美国国债收益率/利率曲线 | `datasets/macro/us-rates-treasury.md` |
| CFTC COT/持仓 | `datasets/macro/cftc-positioning.md` |
| 加密交易所现货/永续/盘口/K线 | `datasets/crypto/exchange-market-data.md` |

## 3. Named-provider/API routes

| Provider/API | Open directly |
|---|---|
| Tencent / 腾讯行情 | `providers/tencent.md` |
| Eastmoney / 东方财富 / 东财 | `providers/eastmoney.md` |
| Sina / 新浪行情 | `providers/sina.md` |
| CNINFO / 巨潮资讯 | `providers/cninfo.md` |
| SHFE / 上期所 | `providers/shfe.md` |
| INE / 上海国际能源交易中心 | `providers/ine.md` |
| DCE / 大商所 | `providers/dce.md` |
| CZCE / 郑商所 | `providers/czce.md` |
| CFFEX / 中金所 | `providers/cffex.md` |
| GFEX / 广期所 | `providers/gfex.md` |
| Yahoo Finance | `providers/yahoo.md` |
| SEC EDGAR | `providers/sec-edgar.md` |
| U.S. Treasury | `providers/us-treasury.md` |
| CFTC | `providers/cftc.md` |
| Binance | `providers/binance.md` |
| Wind / Choice | `providers/wind-choice.md` |
| TradingView | `providers/tradingview.md` |

## 4. Maintenance / audit route

Only when the question is about overall coverage, READY/RECIPE/RESTRICTED inventory, migration, or Skill maintenance, open `references/capability-index.yaml` and related schema/coverage files.

## Escalation rule

If the first-hop card is insufficient, expand one level at a time: **task → dataset → shortlisted provider → detailed reference/recipe**. Do not broaden to unrelated asset classes or enumerate every alternative source unless the user explicitly asks for a comprehensive comparison.
