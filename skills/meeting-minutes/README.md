# meeting-minutes —— 腾讯会议纪要 skill

把零散的会议录音 / 截图 / 笔记整理成逻辑严密、排版精美的正式会议纪要，
配合 `MeetingMinutesFormatter.bas` 宏在 Word 里一键排版。

## 怎么用（一句话触发）

> 用 meeting-minutes：整理这份腾讯会议录音 / 笔记

Codex 按输出规则直接生成带样式标记的纪要正文（Markdown）。在 Word 中
导入 `scripts/MeetingMinutesFormatter.bas`，运行宏 `FormatMeetingMinutes` 即可一键美化。

## 里面有什么

- `SKILL.md` —— 给 Codex 看的工作流（角色设定 + 输出规则 + 排版规范 + 示例）
- `agents/openai.yaml` —— Codex 界面中的展示配置
- `scripts/MeetingMinutesFormatter.bas` —— Word VBA 一键排版宏（v2.0）
