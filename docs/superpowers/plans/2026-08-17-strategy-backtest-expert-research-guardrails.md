# Strategy Backtest Expert Research Guardrails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add lightweight research-definition, data-safety, report-quality and scoped-edit guardrails to `strategy-backtest-expert` without turning it into a rigid research framework.

**Architecture:** Keep the existing upstream snapshot and large `quant-backtest-lab` workflow intact. Put cross-cutting research behavior in the top-level fork `SKILL.md`, extend the existing `common_pitfalls.md` self-check with research-only checks, and update documentation so `financial-data` is the acquisition encyclopedia while this skill owns analysis correctness and reporting.

**Tech Stack:** Markdown Agent Skills, existing Python/pandas backtest references, existing HTML dashboard/report conventions.

## Global Constraints

- No task classifier or mandatory research-type routing.
- No complex schema, report DSL, multi-agent orchestration, or mandatory multi-file research contract.
- Preserve all existing look-ahead, warmup, T+1, lot-size and execution safeguards.
- Do not modify the upstream snapshot `agents/strategy-backtest-expert.md`.
- Formal HTML uses a fixed skeleton with flexible research-profile modules; latest MA-breakdown report conventions are the initial reference.

---

### Task 1: Broaden the top-level skill contract

**Files:**
- Modify: `skills/strategy-backtest-expert/SKILL.md`

- [ ] Update frontmatter description to trigger on quantitative market research/statistical analysis as well as backtests, without summarizing the workflow.
- [ ] Add concise rules for core-definition closure, material semantic clarification, definition-change recomputation, and non-backtest research outputs.
- [ ] Replace hard global provider priority with `financial-data`-first source routing when source/history/methodology decisions matter; keep bundled westock tools as available implementations.
- [ ] Add data-fitness checks, critical-result independent validation, narrative traceability, formal HTML skeleton/profile rules, and scoped-edit protection.
- [ ] Preserve all backtest-specific hard rules by continuing to require `quant-backtest-lab/SKILL.md` for actual strategy backtests.

### Task 2: Extend the existing self-check rather than adding a new framework

**Files:**
- Modify: `skills/strategy-backtest-expert/skills/quant-backtest-lab/reference/common_pitfalls.md`

- [ ] Keep the existing 5 critical backtest checks unchanged.
- [ ] Add a short “Research / statistical analysis addendum — when applicable” covering definition drift, data fitness, key-result independent review, finding-vs-explanation boundaries, report quality, and scoped-edit diff protection.

### Task 3: Update user-facing documentation

**Files:**
- Modify: `skills/strategy-backtest-expert/README.md`
- Modify: `README.md`

- [ ] Explain the division of responsibility: `financial-data` = acquisition encyclopedia; `strategy-backtest-expert` = analysis/research/backtest execution and reporting.
- [ ] Document the fixed HTML skeleton + flexible Profile convention and the non-overengineering boundary.
- [ ] Update repository capability summary so the skill is not described as backtest-only.

### Task 4: Verify the skill changes

**Files:** all modified Markdown files.

- [ ] Confirm frontmatter remains valid and description starts with “Use when”.
- [ ] Confirm no references force task classification, mandatory form filling, or all-metric double calculation.
- [ ] Confirm existing `agents/strategy-backtest-expert.md` is unchanged.
- [ ] Confirm all old backtest safety concepts remain referenced: look-ahead, warmup, T+1/market rules, self-check, dashboard.
- [ ] Confirm new concepts are present: material definition closure, `financial-data`, data fitness, independent key-result review, conclusion→evidence→explanation→boundary, horizontal scroll, folded bottom sheet, scoped-edit diff, finding/interpretation/causality separation.
