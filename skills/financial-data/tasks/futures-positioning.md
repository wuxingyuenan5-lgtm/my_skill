# 国内期货会员成交 / 持仓排名研究

## Objective
研究会员成交量、持多/持空排名、Top5/10/20集中度和排名变化，同时避免把披露子集误解成全市场净头寸。

## Required datasets
- `../datasets/futures/member-position-ranking.md`
- 计算集中度时同时读取 `../datasets/futures/daily-contract-market-data.md` 作为成交量/OI分母。

## Optional datasets
- `../datasets/futures/warehouse-inventory.md`：需要仓单/库存共振时再读。

## Recommended source path
按品种交易所直接进入 SHFE/INE/DCE/CZCE/CFFEX/GFEX provider 卡。当前共享参考实现对 SHFE/DCE/CZCE/CFFEX/GFEX 有 READY fetcher；INE transport 仍需项目独立核验。

## Methodology / caveats
成交榜、持多榜、持空榜是独立榜单；同一rank不代表同一会员。Top-N long-minus-short 是披露子集差值，不是全市场净持仓。未披露可能来自交易所披露门槛，不等于接口故障。

## What to freeze into the downstream project
对应交易所 recipe、scope规则、会员原名、披露状态、Top-N方法、分母口径、last_verified。

## Avoid unnecessary reads
只研究一个品种时不读取六家交易所全部 Provider 卡。