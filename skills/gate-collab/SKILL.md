---
name: gate-collab
description: 多智能体隔空协作工作流（视频《Claude Code 写、Codex 审》模式）：通过独立留言仓库 gate 和操作台 switch，让多个 AI（Codex / Claude Code / WorkBuddy / 子智能体）分角色协作——负责人派活、执行人写代码、审查人挑错、风险全关才收尾。当用户要求"多 AI 分工协作、互相审查、agent 协同、让 A 写 B 审、某个 AI 负责人另一个 AI 执行人"，或想用一个聊天框指挥多个 AI 干活时使用。
---

# gate-collab：多智能体隔空协作

目标：多个 AI 在同一个共享项目里隔空协作（谁都不看谁的窗口、不互相复制粘贴），通过项目里独立的留言仓库（gate）分角色推进：**负责人**派活盯风险，**执行人**改代码，**审查人**挑错，所有风险关闭后才收尾。

## 1. 解析角色
- 负责人（导演）：默认=当前会话；用户说"你负责 / codex 负责人"即是你。
- 执行人（写手）：默认=codex；用户指定 workbuddy / claude / 其他时用对应 AI。
- 审查人：默认=codex，必须与执行人不同上下文。
- 指定了未安装的 AI（如 workbuddy 没有命令）：告知用户，回退成 codex 子智能体扮演，或提示安装后重跑。
- 同时解析**模型**：`codex(gpt-5.6-sol) 负责人` / `--writer-model gpt-5.6-terra` / `codex@gpt-5.6-sol`；用户没指定就用建议默认。
- 默认模型建议（性价比向）：负责人 `codex · gpt-5.6-sol`（决策强、只看摘要用量小）；执行人 `workbuddy`（App 内选）或 `codex · gpt-5.6-terra`（写代码是 token 大头，terra 性价比）；审查 `codex · gpt-5.6-sol` 或 claude 强模型（挑错质量关键，只看 diff）。

## 2. 建项目并派活
1. 用操作台建项目（自动 git init、装 gate、复制 roles/ 和 AGENTS.md）：
   `python3 <skill_dir>/bin/switch.py new <项目名> --dir <位置> --director-ai <负责人> --director-model <模型> --writer-ai <执行人> --writer-model <模型> --reviewer-ai <审查人> --reviewer-model <模型> --no-launch`
   已有目录会自动复用登记。之后所有命令都在项目里跑：`cd <项目> && python3 gate.py ...`。分工与模型会写进项目的 `roles/AI计划.md`，每个窗口开工前先读它。
2. 负责人先发派活留言（任务 / 验收标准 / 节奏）：
   `python3 gate.py send <频道名> "任务：… 验收：…" --type note --author 导演`
   频道名默认=项目名，第一条消息自动建频道。

## 3. 指派执行人与审查人
把 `roles/` 对应文件整份作为对方的角色说明（子智能体首条消息 / 独立终端窗口启动 prompt / 粘贴给 WorkBuddy），附上项目绝对路径和频道名。两人必须独立上下文，自己审自己无效。
- 子智能体模式（本会话直接指挥，推荐）：spawn 两个独立会话，按 `roles/AI计划.md` 的分工用对应模型创建（模型由会话/spawn 参数决定），分别注入 `roles/writer.md`、`roles/reviewer.md`，要求只通过 `gate.py chat/send/status` 沟通，不贴对方回复。
- 窗口模式：`python3 <skill_dir>/bin/switch.py launch --ai <执行人> --role writer`（审查同理）。

## 4. 盯梢与收尾
- 执行人交活：`--type handoff`，固定四段（改了哪些文件 / 跑了什么自证 / 没验证什么 / 最没底什么）。
- 审查人：默认不改代码，一条问题一条 `--type review`（必须带文件行号，并回复交活留言）。
- 用 `python3 gate.py status <频道名>` 盯风险：review 没有对应 fixed 回复就是挂红，必须闭环。审查没动静就催，fixed 没附验证就退回。
- 全部 ✅ 后：`python3 gate.py pr-summary <频道名>`，把摘要交给用户拍板，不替用户做最终决定。

## 纪律
- 负责人不写代码、不直接改文件。
- 消息一律走 gate，禁止把对方回复转贴进自己的上下文（那是作弊，也是这个模式的精髓）。
- 不扩大任务范围；每个 fixed 都要附验证结果。
