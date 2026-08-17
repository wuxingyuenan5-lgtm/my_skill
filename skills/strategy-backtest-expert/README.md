# strategy-backtest-expert（量化研究 / 回测明算 · 自用 fork）

基于 WorkBuddy 内置专家「StrategyBacktestExpert（回测明算）」的个人迭代版。保留原有 Python+pandas 策略回测能力，并增加量化数据研究所需要的定义闭环、数据安全审查、关键结果复核、正式 HTML 研究报告和局部修改保护。

## 来源

- 上游：WorkBuddy 内置专家，本地路径 `~/.workbuddy/plugins/marketplaces/experts/plugins/strategy-backtest-expert/`
- 本目录最初为 2026-08-17 上游快照；`agents/strategy-backtest-expert.md` 保持原文，便于未来 diff。
- 自用规则主要维护在本目录 `SKILL.md` 与 `skills/quant-backtest-lab/reference/common_pitfalls.md`，避免污染上游快照。

## 定位

本 skill 负责**数据拿到以后怎么研究**：

- 核心研究定义与样本口径闭环；
- 描述性统计、事件/状态研究、横截面研究与策略回测；
- 数据是否足以支撑本次分析的安全审查；
- 关键结果独立复核与结果追溯；
- HTML 研究报告的分析、解释、边界与底稿；
- 用户要求局部修改时的未授权区域保护。

它不建立任务分类器，也不要求每个简单问题填写固定研究表单。

## 与 `financial-data` 的分工

同仓库 `skills/financial-data/` 是**金融数据获取百科**，负责：dataset / provider / API / 历史覆盖 / 字段语义 / source routing / fallback / provenance / verified recipe。

本 skill 是**数据分析师**，负责：把选定的数据 recipe 用在研究中，并检查标的身份、覆盖范围、重复/缺失、单位、复权、point-in-time、样本截断等是否真的适用于本次结论。

原则：

> `financial-data` 回答“去哪里、拿什么、怎么安全拿”；本 skill 回答“拿回来后怎么定义、计算、验证、解释和交付”。

本包里的 `westock-data` / `westock-tool` / `neodata-financial-search` 仍是可直接使用的数据工具，但不再被定义为所有市场、所有数据集的永久全局优先级。

## 正式 HTML 约定

采用“**固定骨架 + 灵活 Research Profiles**”：

1. 标题 / 版本 / 数据截止日 / 样本范围；
2. 研究概览；
3. 研究设计 / 方法说明；
4. 核心分析；
5. 综合结论与研究边界；
6. 折叠底稿。

中间分析可按实际问题自由组合事件研究、策略回测、横截面研究、一般统计研究模块，Profile 只是参考，不是分类器。

核心页面应尽量让读者看到“**结论 → 证据 → 解释 → 边界**”。宽表保留有研究意义的字段并横向滚动；完整明细、相关表、长尾样本和辅助统计放在底稿折叠；避免为了视觉简洁删分析，或写大量“请横向滚动”等无研究价值 UI 备注。

当前格式基准来自近期正式研究报告的迭代经验，后续继续在真实项目中逐步优化，而不是一次性设计复杂报告框架。

## 原有回测能力仍保留

真正的策略回测继续使用 `skills/quant-backtest-lab/`：

- 规则型连续策略 / 事件后持有 / 多标的选股 / 组合再平衡；
- A股、港股、美股、ETF、指数；
- look-ahead、warmup、T+1、涨跌停、最小交易单位等市场规则；
- 回测脚本 + equity/trades/summary + HTML dashboard + 结果解读。

如果研究本身没有交易生命周期，不为了满足格式虚构 Sharpe、equity 或 trades。

## 优化指引

| 想改什么 | 改哪里 |
|---|---|
| 研究定义、数据审查、报告原则、局部修改保护 | `SKILL.md`、`skills/quant-backtest-lab/reference/common_pitfalls.md` |
| 交易执行、市场假设、look-ahead | `skills/quant-backtest-lab/SKILL.md`、`reference/*rules*.md` |
| 数据源百科 / provider限制 / verified recipe | 同仓库 `skills/financial-data/` |
| Dashboard / KPI 视觉实现 | `skills/quant-backtest-lab/reference/dashboard_template.html`、`render_dashboard.py` |
| 导出格式 | `skills/quant-backtest-lab/reference/export_results.py` |
| 上游差异 | `agents/strategy-backtest-expert.md`、`README.source.md`（保持快照，不随自用规则改写） |

## 安装

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo wuxingyuenan5-lgtm/my_skill \
  --path skills/strategy-backtest-expert
```

## 合规

- 上游无明确开源许可证，本仓库仅自用迭代、不对外分发。
- 历史统计与回测输出均为模型/样本推演，不构成投资建议。
