# Reference Repository Coverage Matrix

This file is the audit map for the two Apache-2.0 upstream handbooks used for source discovery. `READY` means this repository ships a shared implementation; `RECIPE` means the capability is preserved in the handbook/project-extraction layer; `RESTRICTED` means access/terms/credentials apply.

## `simonlin1212/a-stock-data`

| Upstream capability | financial-data location | State |
|---|---|---|
| mootdx K-line / quote / order book / ticks | `a-share-market-data.md` | RECIPE |
| Tencent quote / PE / PB / cap / turnover / index / ETF | runtime + `a-share-market-data.md` | READY |
| Baidu K-line + MA | `a-share-market-data.md` | RECIPE |
| Eastmoney stock research | `a-share-fundamentals.md` | RECIPE |
| Eastmoney industry research / PDF | `a-share-fundamentals.md` | RECIPE |
| THS consensus EPS | `a-share-fundamentals.md` | RECIPE |
| iwencai NL research search | `a-share-fundamentals.md` | RESTRICTED |
| THS hot stocks / theme attribution | `a-share-microstructure.md` | RECIPE |
| northbound / Connect flow notes | `a-share-flows-positioning.md` | RECIPE |
| sector/concept membership | `a-share-market-data.md` / flows | RECIPE |
| minute/daily stock fund flow | `a-share-flows-positioning.md` | RECIPE |
| Dragon Tiger single-stock / full-market | `a-share-flows-positioning.md` | RECIPE |
| lockup expiry | `a-share-flows-positioning.md` | RECIPE |
| industry ranking / board fund flow | flows + microstructure | RECIPE |
| margin trading | `a-share-flows-positioning.md` | RECIPE |
| block trades | `a-share-flows-positioning.md` | RECIPE |
| shareholder count | `a-share-flows-positioning.md` | RECIPE |
| dividends / bonus / transfer shares | `a-share-flows-positioning.md` | RECIPE |
| stock news / CLS flash / global news | `a-share-research-news.md` | RECIPE |
| quarterly financial snapshot / F10 / stock info | `a-share-fundamentals.md` | RECIPE |
| Sina financial statements | `a-share-fundamentals.md` | RECIPE |
| CNINFO filings + official backups | `a-share-fundamentals.md` | RECIPE |
| limit-up / break-board / limit-down / previous-limit pools | `a-share-microstructure.md` | RECIPE |
| THS limit-up insight/reasons | `a-share-microstructure.md` | RECIPE |
| exchange watch list | `a-share-microstructure.md` | RECIPE |
| intraday severe anomaly pool | `a-share-microstructure.md` | RECIPE |
| China ETF option contract list / T quote / Greeks / IV | `china-etf-options.md` | RECIPE |
| investor IRM | `a-share-research-news.md` | RECIPE |
| THS hot list / EM popularity / concept hits | `a-share-microstructure.md` | RECIPE |
| official Dragon-Tiger fallback | `a-share-source-recipes.md` | RECIPE |
| Sina fund-flow fallback | `a-share-source-recipes.md` | RECIPE |
| official/alternate filing fallback | `a-share-source-recipes.md` | RECIPE |

Preserved upstream pitfalls include BSE 43/83/87 stale codes, Tencent field-index corrections, CNINFO orgId mapping, Eastmoney throttling/domain separation, `diff` list/dict behavior and report ticker normalization.

## `simonlin1212/global-stock-data`

| Upstream capability | financial-data location | State |
|---|---|---|
| US/HK quotes | `global-equity-market-data.md` | RECIPE |
| US/HK K-lines | `global-equity-market-data.md` | RECIPE |
| local MA/EMA/MACD/RSI/KDJ/Bollinger | runtime `indicators.py` | READY |
| Eastmoney/Yahoo fundamentals/valuation | `global-equity-fundamentals.md` | RECIPE |
| analyst targets/estimates/holdings | `global-equity-fundamentals.md` | RECIPE |
| daily fund flow | global equity handbook | RECIPE |
| CBOE chain / Greeks / IV / 0DTE | `us-options.md` | RESTRICTED |
| Yahoo option fallback | `us-options.md` | RECIPE |
| SEC submissions / Company Facts | runtime + SEC handbook | READY |
| SEC Daily Index | `sec-edgar-advanced.md` | RECIPE |
| SEC full-text search | `sec-edgar-advanced.md` | RECIPE |
| SEC Frames market screener | `sec-edgar-advanced.md` | RECIPE |
| FINRA Reg SHO daily short volume | `macro-positioning-events.md` | RESTRICTED |
| US Treasury curve | runtime | READY |
| CFTC COT | `macro-positioning-events.md` | RECIPE |
| Nasdaq earnings calendar | `global-equity-events.md` | RESTRICTED |
| stock search / full-market list | `global-equity-market-data.md` | RECIPE |
| stock news | `global-equity-events.md` | RECIPE |
| ticker ↔ CIK | SEC runtime | READY |

## Beyond the upstream union

`financial-data` additionally includes futures contract/continuous/curve/basis/warehouse/trading-parameter engineering, TradingView/Lightweight delivery, licensed professional source migration, canonical chart data, project extraction and source/capability registries.
