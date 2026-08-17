# Strategy Backtest Expert Research Guardrails Design

## Goal

在不把 skill 变成重型工作流的前提下，将 `strategy-backtest-expert` 从“只会策略回测”扩展为能够可靠执行量化数据研究、事件统计与策略回测的分析 skill，并吸收均线有效跌破统计项目暴露出的定义漂移、数据审查、报告退化和局部修改污染问题。

## Design principles

1. **增加护栏，不增加轨道。** 不引入任务分类器、阶段编排器、复杂 schema 或强制表单。
2. **研究定义先闭环。** 会改变样本、指标含义或结论的核心定义必须在正式计算前明确；只有存在实质语义歧义时才向用户确认。
3. **`financial-data` 管获取百科，本 skill 管分析适用性。** 数据源选择、历史覆盖、provider 约束优先参考 `financial-data`；本 skill 负责确认数据是否足以支撑研究并对后续计算负责。
4. **关键结果可追溯、可复核。** 原始数据→清洗→分析样本/事件→派生指标→统计→图表/正文形成单一链路；重要结论至少有一种独立复核方式，辅助统计不机械双算。
5. **报告固定骨架、内容保持开放。** 正式 HTML 统一采用版本/数据范围→研究概览→研究设计→核心分析→综合结论/边界→折叠底稿；中间模块参考事件研究、策略回测、横截面研究、一般统计研究 Profile，但不得先强制分类。
6. **报告不能退化成纯数据页。** 核心页面优先遵循“结论→证据→解释→边界”；宽表横向滚动，不为简洁删字段；辅助底稿折叠；避免无研究价值的 UI 提示语。
7. **局部修改必须保护未授权区域。** 用户指定只改某些模块时，先明确允许变化范围，修改后对未授权区域做 diff；发现意外变化不得直接交付。
8. **发现与解释分离。** 描述性关系、推断解释和因果结论必须区分；核心结论检查反例或替代解释，避免把条件分布写成因果关系。

## Scope

### Modify
- `skills/strategy-backtest-expert/SKILL.md`
- `skills/strategy-backtest-expert/README.md`
- `skills/strategy-backtest-expert/skills/quant-backtest-lab/reference/common_pitfalls.md`
- repository root `README.md` entry if needed for capability wording

### Preserve
- `skills/strategy-backtest-expert/agents/strategy-backtest-expert.md` remains the upstream snapshot.
- Do not restructure `quant-backtest-lab` or its dashboard implementation in this pass.
- Do not add task classifiers, report DSLs, multi-agent orchestration, or mandatory multi-file research contracts.

## Success criteria

- Top-level skill can be discovered for quantitative market research/statistical analysis as well as backtests.
- It no longer hard-codes one global data-provider priority when `financial-data` can route by dataset/use case.
- Research-definition drift, data-fitness checks, critical-result independent review, report quality and scoped-edit protection are explicit requirements.
- Existing backtest-specific look-ahead, warmup, T+1 and execution safeguards remain intact.
- The change remains concise enough that future agents can follow it without turning every simple analysis into a formal process.
