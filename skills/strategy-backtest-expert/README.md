# strategy-backtest-expert（回测明算 · 自用 fork）

把自然语言交易策略描述转成可运行 Python + pandas 回测的 skill，fork 自 WorkBuddy 市场内置专家
「StrategyBacktestExpert」（回测明算），**个人自用迭代版**，不改动上游。

## 来源

- 上游：WorkBuddy 内置专家，本地路径
  `~/.workbuddy/plugins/marketplaces/experts/plugins/strategy-backtest-expert/`
- 本目录内容为该路径 2026-08-17 的快照（agents/ + skills/ 原样复制），入口 `SKILL.md` 为重新组织的工作流说明。
- `agents/strategy-backtest-expert.md` 保留上游 agent 定义原文，便于日后 diff。

## 能力

- 四类回测形态：规则型连续策略 / 事件研究（事件后 N 天收益）/ 多标的选股 / 组合再平衡
- 全市场：A 股（含 T+1、涨跌停）、港股、美股、ETF、指数
- 数据源：`skills/westock-data`（默认）、`skills/westock-tool`（选股）、`skills/neodata-financial-search`（兜底）
- 交付：回测脚本 + equity/trades/summary 三件套 + HTML 仪表盘 + 图表 + 三段式解读

## 安装

```bash
# Codex
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo wuxingyuenan5-lgtm/my_skill \
  --path skills/strategy-backtest-expert

# WorkBuddy：将本目录复制到 ~/.workbuddy/skills/strategy-backtest-expert/
```

## 优化指引

| 想改什么 | 改哪里 |
|---|---|
| 交易规则、市场假设、look-ahead 处理 | `skills/quant-backtest-lab/SKILL.md`、`skills/quant-backtest-lab/reference/*rules*.md` |
| 仪表盘/KPI 展示 | `skills/quant-backtest-lab/reference/dashboard_template.html`、`render_dashboard.py` |
| 导出格式 | `skills/quant-backtest-lab/reference/export_results.py` |
| 常见陷阱清单 | `skills/quant-backtest-lab/reference/common_pitfalls.md`、`pitfalls/pandas.md` |
| 数据源切换 | `skills/westock-data/`、`skills/westock-tool/`（保持"结构化数据优先、兜底披露来源"原则） |

## 合规

- 上游无明确开源许可证，本仓库仅自用迭代、不对外分发
- 回测输出仅为模型推演，不构成投资建议
