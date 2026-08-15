# CNINFO / China Exchanges / THS / iwencai

## CNINFO

Use for official A-share filings and Investor Relations/互动易. Resolve organization/security mapping from current official mapping rather than synthesizing orgId from ticker; hard-coded orgId patterns have produced silent zero-result failures.

Filings: preserve announcement ID/title/category/publish timestamp/PDF URL and report period separately. IRM: preserve question, answer, ask/reply timestamps and answerer; unanswered questions are legitimate rows, not request failures.

## SSE / SZSE / BSE

Use first-party exchange sources for definitions, notices, official filings, trading rules, abnormal trading/risk lists and, where offered, Dragon-Tiger/market statistics. Web endpoints can change; freeze entry page + parser fixture + verification date. Do not bypass access restrictions.

## THS

Use for vendor consensus EPS, hot stocks, thematic/limit-up reason labels and popularity signals. These are vendor-derived/editorial fields, not legal filings or standardized industry taxonomy. Save provider/methodology and `as_of`.

## iwencai

Useful semantic screening/research search where API access is available. Treat as `RESTRICTED`; store key in environment/secret manager. Exporting a recipe should list required env vars, never embed credentials.
