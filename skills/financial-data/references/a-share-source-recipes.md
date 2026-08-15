# A股 Source Recipe 速查

| Source | 典型能力 | Auth | 风控/注意 | 推荐角色 |
|---|---|---|---|---|
| mootdx/TDX TCP | K线、盘口、逐笔、财务、F10 | 无 | 服务器可握手但无真实数据；需真实 bar probe | 行情底层/本地研究 |
| Tencent | quote、估值、市值、换手、指数/ETF、K线 | 无 | GBK/字段索引；显式市场前缀；旧北交所 stale | 首选公共行情 |
| Sina | quote、财报、日度资金、ETF options | 无/部分需 Referer | GBK/不同 endpoint 格式 | 独立 fallback |
| Eastmoney | 横截面、研报、资金、龙虎榜、解禁、两融、大宗、股东、分红、涨停池 | 无 | 高风控；统一 throttle；不同子域独立 WAF | 独有研究数据 |
| CNINFO | 公告、互动易 | 无 | orgId 映射/接口参数变化 | 官方披露/互动 |
| SSE/SZSE/BSE | 公告、龙虎榜、监控/规则 | 无/网页限制不一 | 以交易所当前条款为准 | 第一方复核 |
| THS | 一致预期、热点、题材、热榜 | 无/部分限制 | vendor-derived | 情绪/研究标签 |
| iwencai | 自然语言研报/筛选 | API Key/SkillHub | Key 只放环境变量 | 主题研究 |
| Wind/Choice | 全量专业金融数据 | 付费许可 | 授权/终端/接口 | 生产/机构优先 |

## Eastmoney request policy

单 session、Keep-Alive；研究批量建议 >=1s 间隔+jitter；429/5xx 退避；403 作为风控信号；每子域独立 health；检查 JSON 业务状态；批量先横截面后本地过滤。

## 上游参考

Apache-2.0 `simonlin1212/a-stock-data` 是本手册重要 endpoint discovery/踩坑来源。项目若直接复制其函数实现，应保留 Apache-2.0 notice/attribution；更推荐把函数重写成项目自己的 provider client + canonical schema。
