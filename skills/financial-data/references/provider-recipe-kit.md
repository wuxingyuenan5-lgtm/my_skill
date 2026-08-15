# Provider Recipe Kit

Use this as the compact copy-ready engineering layer beneath the domain handbooks. Provider endpoints are implementation details: verify them before freezing a new production integration.

## Eastmoney common HTTP helper

Core datacenter endpoint family:

```text
https://datacenter-web.eastmoney.com/api/data/v1/get
```

Common parameters: `reportName`, `columns`, `filter`, `pageNumber`, `pageSize`, `sortColumns`, `sortTypes`, `source=WEB`, `client=WEB`.

Reviewed upstream report names include:

```text
RPTA_WEB_RZRQ_GGMX   financing / securities lending detail
RPT_DATA_BLOCKTRADE  block trades
RPT_HOLDERNUMLATEST  shareholder-count history
RPT_SHAREBONUS_DET   dividends / bonus / transfer shares
RPT_LIFT_STAGE       lockup expiry/history
```

Do not infer a report schema from the name. Freeze raw response fixtures and field maps per report.

Fresh project helper:

```python
import random, time, requests

class EastmoneyClient:
    def __init__(self, min_interval=1.0):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        self.min_interval = float(min_interval)
        self._last = 0.0

    def get(self, url, **kwargs):
        wait = self.min_interval - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait + random.uniform(0.05, 0.25))
        try:
            r = self.session.get(url, timeout=15, **kwargs)
            r.raise_for_status()
            return r
        finally:
            self._last = time.monotonic()

    def datacenter(self, report_name, *, filter_str="", columns="ALL", page_size=50,
                   sort_columns="", sort_types="-1"):
        params = {"reportName": report_name, "columns": columns, "filter": filter_str,
                  "pageNumber": "1", "pageSize": str(page_size),
                  "sortColumns": sort_columns, "sortTypes": sort_types,
                  "source": "WEB", "client": "WEB"}
        payload = self.get("https://datacenter-web.eastmoney.com/api/data/v1/get", params=params).json()
        result = payload.get("result")
        if result is None:
            raise RuntimeError(f"Eastmoney business response missing result: {payload}")
        return result.get("data") or []
```

For Eastmoney `push2/push2his/reportapi/search/np-weblist`, maintain the same throttling principle but separate source-health state by hostname. A 403 is a risk-control signal; hammering retries is not a fallback.

## Tencent quote

```text
https://qt.gtimg.cn/q=sh600519,sz000001,...
encoding: GBK
```

Normalize percentages from percent points to decimal and amounts/capitalization to base CNY. See `a-share-market-data.md` for calibrated fields. Explicit exchange prefixes beat numeric heuristics.

## SEC

```text
https://www.sec.gov/files/company_tickers.json
https://data.sec.gov/submissions/CIK##########.json
https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json
https://data.sec.gov/api/xbrl/frames/<taxonomy>/<tag>/<unit>/<period>.json
```

Set a truthful declared User-Agent/contact; centralize rate limiting. Preserve accession, form, filed/accepted/publish timestamps and exact XBRL tag/unit.

## US Treasury

Use Treasury's official daily rates CSV/data endpoints; parse the date column and each maturity explicitly. Never screen-scrape a rendered chart when a downloadable table is available.

## CFTC COT

Use CFTC public reporting/Socrata datasets; pin the dataset/report family (Legacy/Disaggregated/TFF) and save CFTC contract code. Do not mix report families without a mapping.

## Yahoo

Yahoo public web endpoints can require cookies/crumbs and are subject to provider terms. Keep a reusable session; refresh credentials on expiry; store canonical symbols separately from Yahoo aliases. Use Yahoo as research/fallback unless the project's rights assessment allows more.

## CBOE / FINRA / Nasdaq

These are useful official/provider datasets but access to an endpoint is not equivalent to commercial redistribution rights. Their recipes live in `us-options.md`, `macro-positioning-events.md`, `global-equity-events.md`; freeze current terms with the project.

## Chinese futures exchanges

Prefer official exchange publication for settlement, parameters, warehouse/position/delivery facts. For real-time data use CTP/licensed feed in production. Save entry page + actual endpoint + fixture + verification date rather than relying on a single undocumented path forever.
