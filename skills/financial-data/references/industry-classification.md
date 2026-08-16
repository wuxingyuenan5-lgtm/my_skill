# Industry / Sector / Concept Classification

Industry classification is versioned reference data, not a timeless label.

## China

Keep official/standard taxonomies separately: 申万2021, 中信, CSRC, exchange classifications. Store classification name/version, level, code, effective_from/effective_to and constituent membership dates.

Provider concepts/themes (THS/Eastmoney/Wind concepts) are dynamic vendor tags and must never overwrite standardized industry fields.

## Global

GICS/ICB/NAICS/SIC are distinct systems with licensing and hierarchy differences. SEC SIC can be useful as a public filing classification, but it is not equivalent to GICS.

## Point-in-time membership

Backtests need constituent/membership as-of dates. Current industry or index membership applied to old prices causes survivorship/classification leakage.
