# Fee cheat sheet — three venues, three fee models

Everything below was bound from each venue's own published schedule or live API on 2026-09-27. Fees on
event contracts are the whole game: a 1¢ gross gap is routinely worth −1¢ after vig.

## Kalshi

- **Taker fee:** `ceil( M × 0.07 × C × P × (1−P) )` — rounded **up** to the cent per order, `M` a per-series
  multiplier. The instrument reads `M` live from the `/series` endpoint rather than from the published PDF,
  because the live value is what a trade pays today. Maker fee `M × 0.0175 × …`, with maker `M` defaulting to
  0 on most series; game series are `quadratic_with_maker_fees`.
- **Consequence:** the ceiling makes a **size floor** that depends on the gap. The smallest fee is one cent per
  order, so at five contracts a gap must exceed 0.2¢ per contract just to cover Kalshi's fee; a 0.2¢ gap needs
  about six contracts to break even, a 0.7¢ gap clears at five. Below the floor for its gap, a trade is
  negative after fees however the books look.
- **Books are bids only.** A YES ask is `1 − best NO bid`. Prices are fixed-point dollars; some series tick
  at 0.1¢.
- **Rate limits** are earned, never bought (per Kalshi's published rate-limits page, read 2026-09-27): Basic
  200 read / 100 write tokens per second at signup; Advanced by a self-serve upgrade call with no volume
  requirement; Expert, Premier, Paragon, Prime and Prestige by trailing-30-day volume share, with separate
  earn and keep thresholds. Ten tokens per order.
- Public REST (books, markets, series) answers without a key; the websocket needs a free API key even for
  public channels. A closed market's book answers 404.

## Polymarket (polymarket.com, offshore book)

- **Taker fee:** `C × rate × p × (1−p)`, no rounding, `rate` per market from the market's `feeSchedule`
  (rates seen at the time of binding: NFL 0; the long-dated politics markets 0.04; tennis and MLB 0.05).
  Maker fee 0.
- Books from the CLOB: **asks descending, bids ascending**; never trust wire order. Tick size per market
  (0.1 / 0.01 / 0.005 / 0.0025 / 0.001) and it can change; `min_order_size` 5.
- Off-chain matching, on-chain settlement (Polygon). After an engine restart there is a two-minute
  post-only window.
- **From the United States, polymarket.com refuses trading** ("Trading is blocked in the United States …
  Switch to polymarket.us"). Reads still work, so a scanner sees a book a US resident cannot trade.

## Polymarket US (polymarket.us — QCX LLC, a separate CFTC-regulated exchange)

- Not an account-gated view of the offshore book: a different exchange, different fees, different ticks.
- **Fee:** `Θ × C × p × (1−p)`, taker `Θ = 0.0695` (max $1.74 per 100 contracts at p = 0.50), maker
  **rebate** `Θ = −0.0125`. Rounded to the nearest cent, **banker's rounding, per fill**. Table-tennis taker
  Θ moves to 0.10 on 2026-09-30. Taker rebates of 10 / 25 / 50% above $250k / $1M / $10M prior-month volume.
- Tick 0.01, fractional contracts (minimum 0.01), `feeCoefficient` on every market.
- A public gateway lists events, markets and books without a key; several of the same questions are listed
  here and on the offshore book, so one question can have **three books**.

## Why three rounding rules matter

| venue | rounding | effect on a 0.3¢ fee |
|---|---|---|
| Kalshi | ceiling per order | pays 1¢ |
| Polymarket (offshore) | none | pays 0.3¢ |
| Polymarket US | nearest cent, half-even, per fill | pays 0¢ |

Same formula shape, three different answers on the same trade. Any "arbitrage" number that does not say
which rounding it applied is not a number.
