# 美股期权数据手册

## CBOE delayed quote/options feed

能力：完整链、bid/ask、volume、open_interest、IV、Delta/Gamma/Vega/Theta/Rho、underlying spot。适合研究、0DTE 和 flow 分析；CBOE 内容许可/商业使用需要按当前条款确认/授权。

## OCC/OSI symbol parsing

典型结构：root + YYMMDD + C/P + 8位 strike（千分之一美元）。root 可能含数字，解析不要假设纯字母。

## 0DTE

按美国东部日期判断并正确处理 EST/EDT，不硬编码 UTC-4。

## Flow 派生

`volume/open_interest` 只是一种粗筛选，不能直接等价为新开仓；OI 更新有时滞。put/call ratio、volume-weighted IV、delta exposure 属本地派生，记录算法版本。

## Yahoo fallback

Yahoo options 可取 calls/puts、expiries、bid/ask、volume、OI、impliedVolatility，通常没有完整 Greeks。需要 cookie/crumb 的 endpoint 由 session helper 管理并自动刷新。
