# FX and Crypto Data Handbook

## FX

Instrument identity must specify base/quote (`EUR/USD` != `USD/EUR`), spot/forward/ NDF, venue/fix, and timestamp. Official/reference sources may include central banks and CFETS; executable/trading projects often use broker/ECN/licensed feeds. Preserve bid/ask/mid and fix methodology.

## Crypto spot/perpetual/futures

Exchange-first public APIs (e.g. Binance, Coinbase, OKX) can provide trades, OHLCV, order book, funding, open interest and contract metadata subject to regional/API terms. Distinguish:

- spot symbol;
- linear vs inverse perpetual;
- delivery futures;
- index/mark/last price;
- funding interval/rate;
- quote/base/settlement asset;
- exchange vs consolidated volume.

For cross-exchange spreads, align timestamp, contract denomination and fees/funding. A provider's `BTCUSD` symbol is an alias, not a canonical ID.
