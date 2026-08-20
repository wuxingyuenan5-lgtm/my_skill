# Research Regression Addendum

This addendum captures failure modes found in iterative research projects.

## 1. Context Drift

Long conversations are not a reliable project memory system.

For projects with multiple revisions:

- Keep durable research decisions in `RESEARCH_SPEC.md`;
- Treat chat history as supplementary context;
- Before major revisions, read the current specification and formal baseline first.

## 2. Research Regression

A new version can be technically valid but scientifically worse if it silently returns to an older design.

Before delivery of a major revision, check:

- Is the original research question still answered?
- Are confirmed definitions preserved?
- Are previous analytical improvements retained?
- Did old samples, templates, or conclusions accidentally return?

## 3. Dashboard Drift

A research report can gradually become a database browser:

- More tables;
- More filters;
- More charts;
- Less interpretation.

A formal research page should prioritize:

**Conclusion → Evidence → Interpretation → Boundary**

Interactive components should help readers explore evidence, not replace analysis.

## 4. Scope Protection

When a user requests a local modification:

- Define the modification boundary before editing;
- Protect unrelated sections;
- Avoid full regeneration when a targeted change is requested.

A broader rewrite requires explicit confirmation.
