# 宏观、持仓、短成交量与事件日历

## US Treasury

现有 READY runtime 覆盖收益率曲线及 2Y/10Y/10Y-2Y。

## CFTC COT

官方 public reporting/Socrata API 用于期货持仓结构。常见字段：report_date、market name、CFTC contract code、dealer/asset manager/leveraged funds 或 legacy commercial/non-commercial long/short/spreading。必须明确报表族（Legacy、Disaggregated、TFF 等），不能把不同分类拼成同一时间序列。

## FINRA Reg SHO daily short volume

这是**每日 short sale volume**，不是 short interest。典型字段 Date、Symbol、ShortVolume、ShortExemptVolume、TotalVolume、Market。可派生 `(ShortVolume + ShortExemptVolume) / TotalVolume`，但不能声称是“空头持仓占比”。使用/再分发条款按当前 FINRA 规则核对。

## Nasdaq earnings calendar

用于预期财报事件；字段带 date/time slot/source。供应商 forecast 属 vendor-derived，不是公司指导。
