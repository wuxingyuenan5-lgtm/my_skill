# Futures Curves, Spreads, Basis and Continuous Series

## Term structure

同一时点取同一产品多个真实合约，按到期月排序，保存 quote time、last/settlement 口径、days_to_expiry、volume/OI。盘中 curve 用 last/mid；EOD 研究更适合统一 settlement，不能混用。

## Calendar spread

`spread = near_price - far_price`，并保存 near/far contract IDs。spread 本身可做 synthetic instrument。

## Basis

基差常见 `spot - futures` 或 `futures - spot` 两种符号约定，项目必须显式保存 `basis_definition`，以及 spot source、exact futures contract、单位/币种、税/升贴水/交割地调整。

## Cross-market spread

例如 SHFE CU vs COMEX HG：统一重量单位、FX、税、交割地点/品质、可交易时段，并明确 exact contract vs continuous series。

## Continuous series

连续合约是 derived instrument。保存 roll event table：old/new contract、roll_date、trigger、old/new price、gap、adjustment_factor。

方法至少区分 raw splice、difference/back-adjusted、ratio-adjusted、total-return style。禁止把不同合约原价直接拼接后计算收益而不说明 roll gap。
