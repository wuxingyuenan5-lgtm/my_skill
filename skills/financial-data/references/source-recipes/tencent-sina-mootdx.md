# Tencent / Sina / mootdx Recipe Guide

## Tencent Finance

Best suited to public-research CN quote, index/ETF quote and selected K-line fallback. Shared runtime already implements CN quote normalization.

### Quote
`https://qt.gtimg.cn/q=<provider_symbols>`; GBK; one response per requested symbol. Keep a provider-symbol map (`sh600519`, `sz000001`, `bj920xxx`) separate from canonical ticker.

Critical calibrated fields: 3 price, 4 prev close, 5 open, 31 change amount, 32 change %, 33 high, 34 low, 37 turnover in 万 CNY, 38 turnover %, 39 PE TTM, 43 amplitude %, 44 float cap 亿, 45 total cap 亿, 46 PB, 47/48 limits, 49 volume ratio, 52 static PE.

Never infer market from six digits alone when ambiguity exists. Maintain Shanghai-index whitelist and BSE migration guard.

### K-line
Tencent `ifzq.gtimg.cn` appstock/fqkline family can cover adjusted daily and minute bars. Freeze request parameters/resolution/adjustment and fixture in the downstream project. Upstream testing found a minute response auxiliary field commonly misidentified as turnover; calculate turnover from a verified field set rather than guessing.

## Sina

Use as an independent domain fallback for quote/selected statements/fund flow/options. Many quote endpoints return GBK. Different US/HK/CN/option response layouts require separate parsers.

ETF option endpoints often require a Sina stock/futures Referer. See `china-etf-options.md`.

## mootdx / TDX

Good research/local source for CN K-line, five-level book, ticks, financial snapshot and F10.

- `bars(..., frequency=...)` uses frequency, not a silently ignored category argument.
- raw bars are generally unadjusted; declare adjustment.
- server discovery must validate by fetching actual data, not only TCP connect.
- pin or test library behavior because local BESTIP config/version combinations can fail.

For an institutional production system, CTP/broker/licensed feeds usually replace public/TCP sources while preserving the same canonical schema.
