# Dataset: 国内期货会员成交 / 持仓排名

## What this dataset means
交易所披露的会员成交量、持买单量、持卖单量排名及日变化；是披露排名子集，不是全市场账户穿透持仓。

## Common analytical uses
Top5/10/20集中度、席位变化、资金结构、强弱和拥挤度辅助研究。

## Minimum canonical fields
`trade_date, exchange, scope_type, scope_id, ranking_type, rank, member_raw, member_normalized, value, change, source_url`。

## Frequency and timing semantics
日频、收盘后发布；部分交易所有披露门槛，因此合法无排名与source failure必须分开。

## Recommended sources
直接使用合约所属官方交易所 provider 卡。不要为一个品种扫描六所。

## Alternatives / licensed alternatives
Wind/Choice等授权聚合源。

## Methodology and unit caveats
成交/多头/空头三榜独立，同一rank不代表同一会员。Top-N long-minus-short只是披露子集差值。集中度需同合约总volume/OI分母。

## Source-selection pitfalls
交易所可能更换文件格式、路径或触发WAF；INE当前共享参考只冻结parser，机器transport仍需项目核验。

## Provider cards
`../../providers/shfe.md`, `../../providers/ine.md`, `../../providers/dce.md`, `../../providers/czce.md`, `../../providers/cffex.md`, `../../providers/gfex.md`。

## Copy-ready references
`../../references/futures-positioning-ready-core.md`; reference runtime `../../scripts/financial_data/futures_positioning.py`。