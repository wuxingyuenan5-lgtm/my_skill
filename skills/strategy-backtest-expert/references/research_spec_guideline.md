# Research Spec Guideline

## Purpose

For research projects that will be iterated across multiple rounds, versions, chats, or models, it is usually helpful to maintain a lightweight project-level `RESEARCH_SPEC.md`.

This is a project memory aid, not a workflow engine. Simple one-off analysis does not need one. Even in a long-running project, keep only durable decisions that will matter to future iterations.

## Priority and Flexibility

Use the following precedence when instructions conflict:

1. The user's latest explicit instruction;
2. The current project's confirmed `RESEARCH_SPEC.md` decisions that have not been superseded;
3. The current validated data/code/output for factual results;
4. This skill's generic defaults and suggestions;
5. Older chat history and obsolete report versions.

`RESEARCH_SPEC.md` is a living baseline, not a permanent contract. When the user changes a definition, scope, or report design, follow the new instruction and update the spec afterward.

## What Is Worth Recording

Prefer to record only information whose loss would cause meaningful rework or research drift:

- current formal baseline/version and data cutoff;
- research objective and important scope boundaries;
- definitions that materially change samples or metrics;
- data/sample design decisions that affect interpretation;
- report structure or analytical logic that has been explicitly confirmed;
- durable presentation principles or protected content;
- major version changes and unresolved questions.

Do not turn the spec into a transcript. Temporary layout tweaks, variable names, minor wording edits, or every exploratory idea usually do not belong there.

## Using the Spec During Iteration

At the start of a substantial revision, read the current spec and the current validated baseline before relying on old chat context.

During a major version change, it is useful to note what is added, changed, removed, and intentionally retained. This helps prevent an old template, old sample definition, or discarded interpretation from returning accidentally.

Before final delivery, use the spec as a lightweight regression check rather than a rigid checklist:

- Is the intended research question still answered?
- Did an old definition or old report structure accidentally return?
- Did a report that was meant to be analytical become mainly a database browser?
- Did an important confirmed conclusion disappear into filters or appendices?
- Were unrelated protected sections changed without a good reason?

If the current research problem clearly benefits from a different structure than the spec suggests, prefer the better research design and update the spec rather than forcing the old framework.
