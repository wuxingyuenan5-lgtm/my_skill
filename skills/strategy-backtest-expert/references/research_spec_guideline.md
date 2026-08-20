# Research Spec Guideline

## Purpose

For long-running quantitative research projects, maintain a lightweight project-level research specification (`RESEARCH_SPEC.md`).

It is not a mandatory step for every simple analysis. Use it when a project will involve multiple rounds of iteration, version upgrades, formal reports, or handover across chats/models.

The goal is to preserve research intent and confirmed decisions. Do not use it as a replacement for data, code, or the final report.

## Source of Truth Order

For an iterative research project:

1. Current project `RESEARCH_SPEC.md` — research intent, definitions, design decisions;
2. Current validated data/code/output — factual computation layer;
3. Current report — presentation layer;
4. Chat history — supplementary context only.

Do not rely on long conversation context as the only memory of project decisions.

## Recommended Sections

### 1. Project Status

Record:

- current version;
- data cutoff;
- current formal report;
- data/code location;
- repository commit if applicable.

### 2. Research Objective

Record:

- questions the research is trying to answer;
- decisions or judgments it supports;
- questions explicitly outside scope.

Avoid describing only the data collection task.

### 3. Research Definitions

Record definitions that can materially change results:

- sample unit;
- event/state lifecycle;
- metric anchors and formulas;
- inclusion/exclusion rules;
- incomplete observations and censoring.

### 4. Report Logic

Record:

- page structure;
- what question each page answers;
- key analytical relationships that should be explained.

### 5. Confirmed Design Decisions

Record durable decisions such as:

- analysis versus data lookup separation;
- aggregation versus subgroup comparison rules;
- chart/table presentation principles;
- protected report sections.

Do not record every small visual adjustment.

### 6. Version Changes

For major versions record:

- added;
- changed;
- removed;
- explicitly protected from regression.

## Update Rule

Only write decisions that affect future research iterations:

- New research definition: update;
- New analytical conclusion that changes report logic: update;
- Temporary layout tweak: usually do not update;
- Single typo fix: do not update.

## Regression Review

Before delivering a major revision, compare the output against the research specification:

- Is the original research question still answered?
- Were confirmed definitions preserved?
- Did the report become a data browser instead of an analysis report?
- Were protected sections unintentionally regenerated?
- Did important conclusions disappear into tables or appendices?
