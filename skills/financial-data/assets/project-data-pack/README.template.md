# {{PROJECT_NAME}} data pack

This folder is intentionally independent from the `financial-data` Skill after extraction.

## Frozen capabilities
{{CAPABILITIES}}

## Primary sources
{{PRIMARY_SOURCES}}

## Fallback sources
{{FALLBACK_SOURCES}}

## Required environment variables / entitlements
{{AUTH_REQUIREMENTS}}

## Source health checklist
- Verify endpoint/authentication still works.
- Compare one known symbol/contract against an independent source.
- Check units, timezone/trading day and adjustment methodology.
- Update `last_verified` only after a real check.
- Keep provider credentials out of Git.

## Upgrade rule
If a provider breaks, return to the `financial-data` handbook, choose a replacement recipe, dual-run it where possible, then freeze the new mapping into this project.
