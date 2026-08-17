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

Use these checks for event studies, descriptive/statistical research, cross-sectional analysis, or formal research reports. They supplement the five backtest checks above; they do **not** turn every simple analysis into a mandatory multi-stage workflow.

```text
[ ] A. Definition integrity
    - Re-read the current research definitions, not an older chat/version.
    - Confirm the code uses the same sample unit, event lifecycle, metric anchors,
      denominators, inclusion/exclusion rules, censoring rules and time semantics.
    - If a core definition changed, identify every dependent field/statistic/report
      sentence and recompute the affected chain. Never fix only labels or prose.

[ ] B. Data fitness for this question
    - Verify instrument identity, date coverage, duplicates, missing/truncated data,
      units/currency, adjustment method and relevant close/open/settlement semantics.
    - For point-in-time research, confirm the information was actually available at
      the historical observation/decision date.
    - When source choice, history cap, field semantics or fallback matters, consult
      the `financial-data` skill/source recipe instead of assuming one provider is
      globally preferred.
    - Provider failure is not evidence that the dataset legitimately has no value.

[ ] C. Key-result independent review
    - Pick the results that support the main conclusion and independently recompute
      or cross-check them from a lower layer where practical.
    - The validation path should not merely call the same helper/function again.
    - Do not double-implement every auxiliary statistic; focus on the critical path.

[ ] D. Narrative and report integrity
    - Trace important report numbers back to the validated analysis output/payload;
      do not maintain a second set of hand-entered report numbers.
    - Core pages must contain analysis, not only charts/tables. The reader should be
      able to identify the conclusion, supporting evidence, interpretation and boundary.
    - Keep meaningful wide-table fields and solve width with horizontal scrolling;
      do not silently delete columns or analysis for visual simplicity.
    - Put full event tables, correlation sheets, long-tail samples, quality details
      and other support material in the final/folded research bottom sheet when suitable.
    - Avoid UI-helper prose with no analytical value (for example repeatedly telling
      the reader to scroll horizontally when the interface already makes it obvious).
    - Separate direct findings from interpretation and causality; check obvious
      counterexamples, sample-selection effects or alternative explanations.

[ ] E. Scoped-edit protection
    - If the user asked to modify only named pages/modules/definitions, record the
      allowed-change scope before editing.
    - Diff/hash/compare protected regions afterwards. Any unexpected protected-region
      change must be repaired or explicitly justified before delivery.
    - Never regenerate an older full template and treat accidental regressions as an
      acceptable side effect of a local edit.
```
