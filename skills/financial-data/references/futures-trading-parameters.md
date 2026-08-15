# Futures Trading Parameters, Fees and Sessions

## 动态交易参数

版本化保存 tick size、contract multiplier、order size、daily price limit、exchange margin、broker margin add-on、open/close/close-today fees、last trading day/delivery rules、position limits、session/night session。

“交易所最低保证金”不等于账户实际保证金。期货公司可上浮，临近交割/节假日/异常波动时还会动态调整。

## Trading day semantics

中国夜盘常在前一自然日晚间开始但归属下一交易日。保存 `calendar_timestamp`、`exchange_trading_day`、`session_id`。CTP `TradingDay` 是重要参考，但仍要处理无夜盘、节假日前夜等特殊情况。

## Settlement vs close

期货 EOD 必须区分 last/close 与 settlement。保证金、涨跌停和持仓结算通常围绕 settlement；技术图表可能使用 close。数据模型不要用一个 `close` 覆盖 settlement。
