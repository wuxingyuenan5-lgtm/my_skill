# Fallback Policy

Fallback is a reliability mechanism, not a way to hide failures.

## Independence

Prefer a provider on a different domain and rate-limit/WAF plane. Examples:

- Tencent quote failure → Sina quote before another Tencent endpoint.
- Eastmoney family failure → Tencent/Sina or exchange/official source where the field exists.
- An alternative subdomain of the same provider may be useful operationally, but it is not treated as fully independent evidence.

## Retry

HTTP helper defaults to finite timeout and at most two retries for transient 429/5xx responses. Authentication/access blocks are classified rather than hammered with repeated requests. No infinite retry loops.

## Result semantics

- Primary success: `status=ok` unless quality flags require degradation.
- Primary failure + independent fallback success: `status=degraded`, record `fallbacks_used` and the original error.
- All routes fail: `status=failed` with classified errors.
- Empty provider payload caused by failure is not a successful empty dataset.
- Genuine empty business result (for example no filing matching a valid filter) must be distinguishable from transport/parser failure.

## Health feedback

Classified failures update process-local source health. Transient success can restore runtime health; durable deprecation/block status is controlled by reviewed registry metadata.
