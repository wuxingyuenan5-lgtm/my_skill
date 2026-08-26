# Common Mistakes and Correct Patterns — Index

Read `reference/pitfalls/pandas.md` before writing code. After the code is written, run the checklist below.

## Self-Check Checklist (5 Critical Checks)

Every item includes a concrete verification method. **You must actually execute the check; do not just tell yourself "I checked it."**

```python
"""
[ ] 1. Query alignment: compare the code line by line with the user's original request.
       Check whether buy/sell conditions, position sizing, stop-loss / take-profit,
       execution timing, and stock universe all match the request. Any parameter
       that the user did not explicitly specify but the code had to choose anyway
       must be explained in the final reply.

[ ] 2. No future data: grep the code for every `shift(-` and `iloc[i+` pattern.
       Any hit is a look-ahead bug. This includes signal generation, size
       calculation, stop prices, and take-profit prices — not just the signal lines.

[ ] 3. size > 0: grep all order-placement logic. Every such block must be guarded
       by `if size > 0:` immediately above it; otherwise, high-priced stocks +
       small capital will silently produce size=0 and no trade.

[ ] 4. Warmup segment is correct (mandatory for indicator strategies; all three together):
       (a) Data-loading start < evaluation start — grep the data-source call and
           confirm the start date is moved earlier (MA120 ≈ 180 days,
           EMA200 ≈ 300 days)
       (b) Gate trading side effects before the evaluation start — grep the
           backtest loop and confirm:
           - Allowed: indicators, streak counters, `highest_since_entry`,
             state-machine counters
           - Forbidden: `pending_buy/pending_sell`, cash/position changes,
             `trade_history.append(...)`, `equity_curve.append(...)`
           - `if pd.isna(...)` alone is not enough; the evaluation-start gate
             must still be explicit
       (c) export_results passes start/end — grep `export_results\(` and
           confirm both start and end are explicitly passed. If omitted,
           Sharpe / annualized return will be calculated over the full span,
           including warmup.

[ ] 5. Output language is consistent: dashboard, matplotlib chart titles,
       custom_html modules, and the final reply must all use the same language.
       A Chinese query must not produce English module titles, and an English
       query about Chinese stocks must still produce English output; showing the
       ticker code is the default safe choice.
"""
```

## Research / Statistical Analysis Addendum — When Applicable

Use these as review prompts for event studies, descriptive/statistical research, cross-sectional analysis, or formal research reports. They are intentionally lighter than the backtest hard checks above: apply the parts that matter to the current problem, and do not turn every simple analysis into a mandatory multi-stage workflow.

```text
[ ] A. Definition integrity
    - Re-read the current research definitions, not an older chat/version.
    - Confirm the code uses the same sample unit, event lifecycle, metric anchors,
      denominators, inclusion/exclusion rules, censoring rules and time semantics.
    - If a core definition changed, identify dependent fields/statistics/report
      conclusions and recompute the affected chain. Never fix only labels or prose.

[ ] B. Data fitness for this question
    - Check the data properties that can materially affect this conclusion:
      instrument identity, coverage, duplicates/missing/truncated data, units,
      adjustment method and relevant close/open/settlement semantics.
    - For point-in-time research, confirm the information was actually available at
      the historical observation/decision date.
    - When source choice, history cap, field semantics or fallback matters, consult
      the `financial-data` skill/source recipe instead of assuming one provider is
      globally preferred.
    - Provider failure is not evidence that the dataset legitimately has no value.

[ ] C. Key-result review
    - For formal or high-impact research, independently recompute or cross-check the
      few results that carry the main conclusion where practical.
    - Prefer a lower-level or logically different validation path; do not merely call
      the same helper again.
    - Auxiliary statistics do not need mechanical double implementation.

[ ] D. Narrative and report integrity
    - Important report numbers should trace back to the validated analysis output;
      avoid maintaining a second set of hand-entered report numbers.
    - In a formal narrative report, the main findings should still be understandable
      without requiring the reader to click every filter or subgroup selector.
    - Prefer the正文 to explain the overall pattern, important subgroup differences,
      interpretation and boundary; let filters/tables handle drill-down detail.
    - If obviously heterogeneous groups differ materially, consider group-level
      statistics before treating a pooled sample as the main answer.
    - If a binary signal comes from an underlying continuous variable (distance,
      speed, intensity, valuation, concentration, etc.), consider whether a gradient
      or binning view contains useful information before collapsing it to 0/1.
    - Wide tables with meaningful detail often work better with horizontal scrolling
      than deleting columns solely for layout. Full event tables, long-tail samples,
      quality details and other support material can move to folded bottom sheets.
    - Avoid UI-helper prose with no analytical value, and keep direct findings,
      interpretation and causality distinct.

[ ] E. Iteration / research regression
    - For an iterative project with `RESEARCH_SPEC.md`, read the current spec and
      validated baseline before relying on old chat context.
    - The user's latest explicit instruction supersedes an older spec; update the spec
      after a durable decision changes rather than forcing an obsolete framework.
    - If the user requested a local edit, protect unrelated sections unless a linked
      definition/data change genuinely requires broader updates.
    - Watch for research regression: old samples, old templates, discarded definitions,
      or a report gradually becoming a database browser instead of an analysis report.
    - For major revisions, it is often useful to generate/update the research overview
      after the core analysis pages have stabilized.

[ ] F. Delivery truthfulness
    - If a remote artifact, report, or archive is part of delivery, verify that the
      remote object actually exists and is plausibly complete; check size/hash when
      practical.
    - A successful API response, filename, manifest, or repository path is not by
      itself proof that a large artifact was transferred intact.
```
