# Compliance and Access Policy

Financial data rights vary by source and can change. Source authority and usage permission are separate dimensions.

## Core rules

- Do not bypass CAPTCHA, authentication barriers, access controls, robots restrictions, or explicit anti-scraping terms.
- Do not hard-code credentials, cookies, API keys or personal identities.
- Re-check current terms before commercial use, redistribution or embedding data in a product.
- A public URL or an official organization does not automatically imply unrestricted redistribution.
- Prefer official/government sources when they are both authoritative **and** suitable for the intended use.

## v0.1.0 posture

- SEC EDGAR / US Treasury / CFTC: modeled as high-authority government data; still obey automated-access requirements and current policies.
- SEC automated requests require a truthful `SEC_CONTACT` used in the User-Agent.
- Tencent / Sina / Eastmoney / Yahoo: modeled for research workflows with restricted/uncertain commercial redistribution; verify before business deployment.
- CBOE: official options source but licensing/approval constraints apply; registry-only in v0.1.0.
- FINRA: published short-volume data but scripted/commercial terms require verification; registry-only in v0.1.0.

The classifications were informed by the reviewed upstream projects and source policies available during design. They are metadata, not legal advice and not a permanent license determination.
