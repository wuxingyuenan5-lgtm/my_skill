# Provider: Binance official APIs

last_verified: 2026-08-16
official_reference: https://developers.binance.com/en/docs/products/spot/rest-api

## Identity
Official Binance API source for spot and derivatives market/account/trading data. Use only the product/API family relevant to the project and user region.

## Access and authentication
Spot endpoints with security type `NONE` are public market data; secured endpoints require API key/signature as documented. Binance documents a market-data-only base endpoint for public spot data. Account/trading permissions and regional availability are separate constraints.

## Technical request limits
Do **not** hard-code one global QPS. Binance states current Spot limits are exposed in `/api/v3/exchangeInfo` `rateLimits` and response weight headers; endpoints have different weights. HTTP **429** indicates rate-limit breach; clients must back off. Continuing after 429 can lead to automated IP ban with HTTP **418**; `Retry-After` is provided. Limits are IP-based for request weight. Freeze the observed `exchangeInfo` limits in the downstream project and refresh them.

## Data-range limits
Endpoint-specific; Kline/trade/depth limits and historical windows differ across Spot, USDⓈ-M, COIN-M and Options. Backfill by documented pagination rather than assuming unlimited single requests.

## Freshness and publication timing
24/7. Endpoint data source may be Matching Engine, Memory or Database with different delay characteristics. Use WebSocket streams for streaming workflows when appropriate.

## Licensing and redistribution
API use is subject to Binance Terms, market/product availability and jurisdiction. Public endpoint access does not override regional restrictions or grant unrestricted redistribution rights.

## Data-quality limitations
Separate spot/perpetual/delivery markets; mark/index/last price, base/quote volume, contract size and funding interval are distinct. Handle delistings and symbol status from exchange metadata.

## Copy guidance
See `../datasets/crypto/exchange-market-data.md`, `../references/fx-crypto.md`. Freeze product base URL, `exchangeInfo`, endpoint weights/limits, symbol metadata, retry/Retry-After behavior and regional assumptions; never copy account secrets into the Skill.