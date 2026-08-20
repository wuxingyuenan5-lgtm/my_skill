# my_skill

Personal Codex skills repository.

## Layout

```text
skills/
  <skill-name>/
    SKILL.md
    agents/openai.yaml
    scripts/        # optional reusable tools
    references/     # optional long instructions
    assets/         # optional templates and media
scripts/
  validate_skills.py
```

Keep each skill self-contained under `skills/<skill-name>/` so it can be installed, reviewed, and iterated independently.

## Included Skills

- `gate-collab`: multi-agent collaboration workflow using a shared gate message channel.
- `meeting-minutes`: 腾讯会议纪要整理，配合 VBA 宏在 Word 中一键排版美化。
- `morning-meeting-minutes`: 晨会录音/截图转单页紧凑版会议纪要。
- `financial-data`: financial-data acquisition encyclopedia — dataset/provider/API routing, source constraints, normalization, validation, fallback, provenance and verified retrieval recipes.
- `strategy-backtest-expert`: 量化数据研究 / 事件统计 / 策略回测（fork 自 WorkBuddy「回测明算」专家，个人迭代版）— 负责研究定义、数据适用性审查、可复核计算、正式 HTML 研究报告和策略回测；数据源百科优先与 `financial-data` 协同。
- `resume-autofill-agent`: 简历自动填写 Agent（fork 自 CCC-Zach/resume-autofill-agent，MIT）— 从简历和证明材料建立可溯源的求职者资料，按队列处理网申，通过浏览器自动化填写招聘/升学表单，保存已核验草稿，最终提交须人工确认。

## Install A Skill

Install one skill from this repo:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo wuxingyuenan5-lgtm/my_skill \
  --path skills/gate-collab
```

After installing, start a new Codex turn so the skill list refreshes.

## Maintain Skills

1. Add each new skill as `skills/<skill-name>/SKILL.md`.
2. Keep `SKILL.md` frontmatter minimal: `name` and `description`.
3. Put reusable code in `scripts/`, long conditional context in `references/`, and templates/media in `assets/`.
4. Update this README's skill index when adding or renaming skills.
5. Run validation before committing:

```bash
python3 scripts/validate_skills.py
```
