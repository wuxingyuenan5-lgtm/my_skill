# Global and China Macro Data Handbook

Macro data requires vintage/availability semantics. A release can be revised; storing only observation date creates look-ahead in backtests.

## United States

Primary source families: Federal Reserve/FRED for rates/monetary series, Treasury for yield curves/fiscal debt tables, BLS for CPI/PPI/labor, BEA for GDP/PCE/national accounts, Census for trade/retail/housing, CFTC for positioning. Prefer official APIs/downloads over portals.

## China

Primary source families: National Bureau of Statistics (GDP/CPI/PPI/industry/investment/retail), PBOC (money/credit/TSF/rates/FX reserves), SAFE (BOP/FX/cross-border), Ministry of Finance (fiscal), Customs (trade), ChinaMoney/CFETS/CCDC for interbank rates/bonds/FX where licensing/access permits.

## Europe/global

ECB/Eurostat, BOE, BOJ, IMF, World Bank, OECD/BIS are canonical source families for cross-country macro. Dataset codes/SDMX/API versions must be frozen in project source config.

## Standard macro record

```yaml
series_id:
observation_period:
value:
unit:
frequency:
seasonal_adjustment:
published_at:
available_at:
revision_or_vintage:
source_id:
retrieved_at:
```

Release calendar and actual series are separate datasets. When a news release changes a value, keep prior vintage if the project supports historical simulation.
