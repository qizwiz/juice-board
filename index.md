# Juice Board

A public instrument that prices the same event on two prediction-market venues the way a Kelly gambler
prices it: after both venues' fees, at the size the quoted depth actually holds, against the carry on
the capital it would lock. It reports what it *examined*, not just what it found.

- **[The board](board.html)** — the live-ish snapshot (republished every 10 minutes). Pairs are anonymised
  on the public board; verdicts, prices, vig, depth and reasoning are real.
- **[Track record](track-record.md)** — two pre-registered experiments, sealed before the first row,
  scored as written, including the refutation.
- **[Fee cheat sheet](fees.md)** — three venues, three fee models, bound from each venue's own docs.
- **[Engineering](engineering.md)** — the verified kernel, live-tunable parameters, and what latency costs.

## The one-line result so far

**No executable edge at scan speed.** Over 244 scans of 16 long-dated pairs, 25.3% of rows showed a combined
price under $1, but every one of them was a gap paying between 0.1% and 1.1% a year on capital locked until
2028–29. Over 716 scans of 19 short-dated pairs (settling within 14 days), **2 of 12,481 rows** priced under
$1: both were one-scan crosses during live games, gone within 25 seconds. The gaps that persist, persist
because they are worthless; the gaps that would pay do not persist. Details and denominators on the
track-record page, with both experiments' scored results.

## Why publish a negative result

In a survey of paid prediction-market "arbitrage alert" products made on 2026-09-27 (four products, marketing
pages read, none subscribed to), each stopped at *opportunities detected*; I found none that published
fill-level, fee-inclusive results with a denominator. That is a bounded observation, not a claim about every
product that exists. This page exists to be one counterexample: the method is the product. Nothing here is
trading advice; nothing here trades.
