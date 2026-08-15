# SEC / Yahoo / US Provider Recipes

## SEC EDGAR

Primary official layer for US filings/XBRL. Use truthful User-Agent/contact, centralized rate limiting and accession-aware URLs. Core paths are listed in `provider-recipe-kit.md`; advanced Frames/daily index/FTS in `sec-edgar-advanced.md`.

## Yahoo Finance

Research convenience for US/HK K-lines, quoteSummary fundamentals/consensus/holdings, options and news. Build a session helper that can obtain/refresh cookie+crumb only when the chosen endpoint needs it. Chart endpoints may have different auth behavior from quoteSummary/options.

Always record raw module/tag, currency, `as_of`, period and provider alias. Yahoo terms are restrictive; keep it research-only unless the project's rights review says otherwise.

## CBOE

Options chain/Greeks/IV can be technically accessible from delayed quote feeds, but data/content licensing is separate. Keep CBOE capability `RESTRICTED`. Parse OCC/OSI contract symbol without assuming root is letters only; use America/New_York date/DST for 0DTE.

## FINRA

Reg SHO daily short-volume files: downloaded regulatory dataset. Short volume is not short interest. Verify current automation/commercial terms before deployment.

## Nasdaq

Earnings calendar is useful event metadata but provider terms may constrain use. Treat as restricted until the downstream project's rights review approves it.
