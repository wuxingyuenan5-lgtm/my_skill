# 衍生品数据总入口

衍生品以 exact contract identity 为核心。期权与期货不得只用 underlying/root 代替真实合约。

## 专题

- `us-options.md`：CBOE chain、IV、Greeks、0DTE、flow；Yahoo fallback。
- `china-etf-options.md`：50ETF/300ETF/科创50ETF/500ETF 等 T型报价、OI、Greeks/IV。
- `futures-contract-master.md`：期货合约身份。
- `futures-curves-basis.md`：期限结构、价差、基差、连续合约。

## 统一期权字段

underlying、exchange、expiry、call_put、strike、multiplier、bid/ask/last、volume、open_interest、IV(decimal)、Delta/Gamma/Vega/Theta/Rho、spot/reference time。

Greeks/IV 必须标记 `provider_computed` / `exchange_computed` / `local_model`。不同模型参数下的 Greeks 不自动可比。

0DTE 使用交易所本地日期；美股注意 America/New_York DST。volume/OI、put/call、skew、net delta 都是 derived signal，不是交易者意图事实。
