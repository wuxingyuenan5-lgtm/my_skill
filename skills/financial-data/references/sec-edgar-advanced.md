# SEC EDGAR 高级数据手册

SEC 是美股法定披露与结构化基本面的核心官方源。自动访问必须声明真实 User-Agent/contact，并遵守 SEC 当前 automated access policy/rate limits。

## 1. Submissions

`https://data.sec.gov/submissions/CIK##########.json`：最近 filings 的 form、filingDate、accessionNumber、primaryDocument、description。

## 2. Company Facts

`https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`：保留 taxonomy、tag、unit、start/end、val、form、filed、fy/fp、frame。跨公司/跨期处理 tag equivalence，而不是只写死一个 Revenue tag。

## 3. EDGAR Frames

Endpoint family: `https://data.sec.gov/api/xbrl/frames/<taxonomy>/<tag>/<unit>/<period>.json`。用于单个 XBRL tag 全市场横截面，例如季度 R&D、净利润、资产。

关键点：instant vs duration period 命名不同；同一经济指标可能多个 tags；单位纳入 query；输出保留 cik/entity/location/end/value/accn/fy/fp/form/filed/frame。

## 4. Daily filing stream

EDGAR daily/master index 可用于当日 Form 4 / 8-K / 13F / 144。按日期拉 index，解析 CIK/company/form/date/filename，再按 watchlist/ticker map 过滤。

## 5. Full-text search

用于跨 filings 搜关键词。搜索只是 discovery；最终证据回到 filing document/accession。

## 6. Point-in-time

```text
report_period/end  财务事实对应期间
filed              filing date
accepted_at        SEC 接收时间（若可得）
available_at       回测允许使用时间
retrieved_at       本系统抓取时间
```

禁止用 report period end 代替 available_at。
