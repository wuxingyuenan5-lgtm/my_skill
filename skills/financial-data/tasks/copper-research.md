# 铜 / 铜产业链研究数据路线

## Objective
支持 SHFE/INE/COMEX/LME 铜价格、期限结构、库存/仓单、资金结构以及铜矿股联动研究。

## Required datasets
- 国内铜期货：`../datasets/futures/daily-contract-market-data.md`
- 需要席位时：`../datasets/futures/member-position-ranking.md`
- 需要仓单时：`../datasets/futures/warehouse-inventory.md`

## Optional datasets
- 海外期货与LME数据：见 `../references/futures-source-recipes.md`，多数生产级实时/历史数据涉及授权。
- 铜矿股行情：`../datasets/cn-equity/kline.md` 或 `../datasets/global-equity/kline.md`。
- 公司产量/资源量/副产品暴露：按上市地公告/SEC/交易所披露单独取数。

## Recommended source path
国内优先 SHFE/INE 官方；海外根据 CME/LME/授权供应商条件选择。股票端再进入对应 equity dataset，不提前加载。

## Methodology / caveats
跨所铜价比较必须统一币种、重量单位、税、升贴水、地点、交易时点和合约月份。矿企股价不能简单视为铜Beta，还受金/钴/钼、副产品、成本、汇率和估值影响。

## What to freeze into the downstream project
合约/单位桥、汇率与税费规则、交易所 recipes、库存口径、公司暴露字段、last_verified。

## Avoid unnecessary reads
只在确实做股票联动时读取股票基本面；只做国内铜期限结构时无需加载海外源。