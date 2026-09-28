# Juice Board

A public instrument that prices the same event on two prediction-market venues the way a Kelly gambler
prices it: after both venues' fees, at the size the quoted depth actually holds, against the carry on
the capital it would lock. It reports what it *examined*, not just what it found.

- **[The board](board.html)** — the live-ish snapshot (republished every 10 minutes). Pairs are **unnamed**
  on the public board; verdicts, prices, vig, depth and reasoning are real. Unnamed is not anonymous: both
  venues' order books are public, so a reader who matches a row's prices against them can work out which
  market it is. The names are withheld as a courtesy to the work, not as a secret the page can keep.
- **[Track record](track-record.md)** — three pre-registered experiments, sealed before the first row,
  scored as written, including the refutations.
- **[Fee cheat sheet](fees.md)** — three venues, three fee models, bound from each venue's own docs.
- **[Engineering](engineering.md)** — the verified kernel, live-tunable parameters, and what latency costs.

## The one-line result so far

**No executable edge at scan speed.** Over 244 scans of 16 long-dated pairs, 25.3% of rows showed a combined
price under $1, but 967 of those 976 rows were four pairs sitting permanently under $1 and paying between
0.1% and 1.1% a year on capital locked until 2028–29, and the other nine were one pair flickering; none beat
a 4% hurdle. Over 716 scans of 19 short-dated pairs (settling within 14 days), **2 of 12,481 rows** priced under
$1: both were one-scan crosses during live games, gone within 25 seconds. The gaps that persist, persist
because they are worthless; the gaps that would pay do not persist. Details and denominators on the
track-record page, with both experiments' scored results.

## Why publish a negative result

On 2026-09-27 I read the marketing and pricing pages of four paid prediction-market "arbitrage alert" products
(none subscribed to). Those pages advertise *opportunities detected*; they are not the products' results pages,
so this site makes no claim about whether any of them publishes a track record. What is bound: none of the four
open-source Kalshi/Polymarket bots examined by an independent review of this site publishes any result, fill
count or denominator, and each omits or mis-models at least one venue's fee. This page exists to be one
counterexample: the method is the product. Nothing here is trading advice; nothing here trades.
