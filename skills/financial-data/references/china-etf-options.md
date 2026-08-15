# 中国 ETF 期权数据手册

参考公共研究源可覆盖 50ETF、300ETF、科创50ETF、500ETF 等合约列表、T型报价、OI、行权价、成交量，以及供应商/交易所预计算 Greeks/IV。

## Sina research recipe

Sina `hq.sinajs.cn` option quote family 常见特征：GBK、逗号分隔、需要 `Referer: https://stock.finance.sina.com.cn/`。不同接口分别提供合约月份/认购认沽代码列表、`CON_OP_...` T型报价、`CON_SO_...` Greeks/IV。

上游记录过 Greeks 原始数组空字段偏移问题；项目必须用 fixture 校准字段位置。IV 标准化为 decimal。保留 open_interest、strike、expiry、call_put、trade_code、theoretical value。

## 生产级来源

交易所/券商授权期权行情优先于公共网页接口。希腊值标明是交易所/供应商计算还是本地模型计算，不能混用。
