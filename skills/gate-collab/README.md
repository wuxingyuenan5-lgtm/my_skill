# gate-collab —— 多智能体隔空协作 skill

一句话把"多 AI 分工协作"变成自动流程：你说任务和角色，Codex 自动建项目、派活，
让执行人和审查人通过独立留言仓库（gate）隔空协作，风险全关后给你 PR 摘要。

## 怎么用（一句话触发）

> 用 gate-collab：做一个 Python 计算器，codex 负责人，workbuddy 执行人

Codex 会自动：
1. 用 switch.py 建协作项目（自动 git init + 装 gate + 角色提示词）
2. 当前会话当负责人派活；执行人、审查人各开独立上下文（子智能体或独立窗口）
3. 执行人干完交活（固定四段），审查人逐条挑错（带文件行号）
4. 风险全部关闭 → 生成 PR 摘要给你拍板

## 里面有什么

- `SKILL.md` —— 给 Codex 看的工作流
- `bin/gate.py` —— 消息总线（独立留言仓库，.gate/ 下独立 git + JSONL + 锁）
- `bin/switch.py` —— 操作台（建项目 / 开窗口 / 看进度 / 风险 / PR 摘要）
- `roles/writer.md`、`roles/reviewer.md`、`roles/orchestrator.md` —— 三个角色提示词

## 手动命令（不想要自动流程时）

cd 进项目后：

- `python3 gate.py send 频道 "内容" --type handoff|review|fixed --author 角色名`
- `python3 gate.py chat 频道` / `status 频道` / `pr-summary 频道`

## 角色约定

- 负责人（导演）：不写代码，负责派活、盯风险、把关。
- 执行人（写手）：改代码、跑测试，交活用固定四段。
- 审查人（审查）：默认不改代码，一条问题一条留言，必须带文件行号。

## 选 AI 和模型

一句话里可以带上模型：`codex(gpt-5.6-sol) 负责人，workbuddy 执行人`。
没写就用建议默认：负责人 `codex · gpt-5.6-sol`，执行人 `workbuddy`（App 内选）或
`codex · gpt-5.6-terra`，审查 `codex · gpt-5.6-sol`。分工和模型会写进项目的
`roles/AI计划.md`，每个窗口开工前先读。
