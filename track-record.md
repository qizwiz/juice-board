# Track record

Both experiments were **pre-registered**: hypotheses, gates and the scoring rule were written and sealed
before the first observation. The pre-registration files are private for now (they name the pairs); their
SHA-256 digests are published here so the text can be verified later against what was sealed today.

| experiment | sealed | pre-registration sha256 (prefix) |
|---|---|---|
| 1 · long-dated pairs (settle 2028–29) | 2026-09-27 | `5599869f2a665e81` |
| 2 · short-dated pairs (settle ≤ 14 days) | 2026-09-27 | `e4ae1339c609d0e5` |

## Experiment 1 — long-dated pairs

**Question.** Do cross-venue gaps (Kalshi YES + Polymarket NO priced together under $1, after fees, at
executable depth) survive long enough to execute?

**Gates, scored as written at G1 (244 scans, 16 pairs, 3,863 clean rows, 7 fetch errors):**

| gate | result |
|---|---|
| G2 · rows under $1 at minimum size | 976 / 3,863 (25.3%) |
| G2 · rows under $1 at ≥ $5 depth | 1,219 / 3,863 (31.6%) |
| G3 · persistence of sub-$1 windows | 11 windows, median 9 scans, 6/11 lasted ≥ 3 scans |
| H_adv (gaps collapse within one scan) | **refuted** |
| H_opt (≥ 25% of windows last ≥ 3 scans) | **met** |

**What the gates could not say.** The 976 rows were not fleeting windows. They were **four pairs that
priced under $1 on every scan** for five hours, stable to four decimals, with ≥ 500 contracts of depth on
every row. The "11 windows" are those four permanent gaps cut by the seven fetch-error scans, plus one
fifth pair that flickered under $1 on 9 of its 238 scans.

**Carry, read post hoc and labelled as such.** 0 of 976 sub-$1 rows beat a 4%/yr hurdle on the capital
they lock. The best pays 2.27¢ per contract, about $11 on ~$490 locked for 773 days: **1.1% a year**. The
other three pay 0.1–0.4%.

**Interpretation.** The pre-registration tested the wrong constraint. Persistence was never the binding
limit; carry is. The gaps persist *because* they are worthless.

## Experiment 2 — short-dated pairs

**Question.** Where carry is negligible (settlement within 14 days), do cross-venue gaps exist at all?

**Status at 616 scans, 19 pairs, 10,781 clean rows:** rows under $1 at minimum size **0 / 10,781**; at
≥ $5 depth **0 / 10,781**; no sub-$1 window observed. Every short-dated pair has priced 1–4¢ *over* $1
combined on every scan.

## Settlement divergence (the risk the two-leg trade actually carries)

A pair is only an arbitrage if both venues settle on the same fact. Measured on settled history:

| series | divergent settlements |
|---|---|
| MLB games | 0 / 807 |
| ATP tennis | 1 / 453 |
| WTA tennis | 0 / 540 |

The first live pair to retire settled identically on both venues, 26 minutes apart.

## Method notes

- Fees per venue from each venue's own schedule (see the [fee sheet](fees.md)); depth walked level by
  level; a book too thin for the minimum size prices as *none*, never as a partial.
- Error rows are neutral to persistence windows; the scan interval is derived from the data, not assumed.
- Numbers on this page are the sealed scores. The board republishes live; live counts drift as pairs retire.
