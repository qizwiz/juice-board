# Track record

Both experiments were **pre-registered**: hypotheses, gates and the scoring rule were written before the
first observation, and both have now been **scored** against those gates. The files are private for now
(they name the pairs); their SHA-256 digests are published so the text can be checked later against what
exists today. Each digest covers the file as it stands, pre-registration plus its scored result section.

| experiment | pre-registered | scored | sha256 of the file (prefix) |
|---|---|---|---|
| 1 · long-dated pairs (settle 2028 or later; two close in 2045) | 2026-09-27 | 2026-09-27, at 244 scans | `5599869f2a665e81` |
| 2 · short-dated pairs (settle ≤ 14 days) | 2026-09-27 | 2026-09-27, at 716 scans | `cb5df22999b47ea9` |

Experiment 2's scoring gate (100 scans) fell hours before anyone scored it; the result section says so.

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

**Gates, scored as written at 716 scans (19 pairs, 12,481 clean rows, 65 fetch errors):**

| gate | result |
|---|---|
| G2 · rows under $1 at minimum size | 2 / 12,481 (0.016%) |
| G2 · rows under $1 at ≥ $5 depth | 2 / 12,481 |
| G3 · persistence of sub-$1 windows | 2 windows, median 1 scan, 0/2 lasted ≥ 3 scans |
| H_adv (gaps collapse within one scan) | **supported** |
| H_opt (≥ 25% of windows last ≥ 3 scans) | **not met** |

**What the two rows are.** Both are games that were **in play** that afternoon, each under $1 for exactly
one scan: one at $4.94 all-in for five contracts (1.2¢ per contract, depth up to 210 contracts on that scan),
one at $4.99 for five (0.2¢ per contract, depth up to 500). Both were gone by the next scan, about 25 seconds
later. Settlement was hours away, so carry is beaten trivially and means nothing here.

**Interpretation.** Where carry is negligible, cross-venue gaps do appear, as one-scan crosses while a live
game moves the two books at different speeds, and they close within the scan interval. Whether any of them
is capturable is a latency question (feed, decision, two orders), not a pricing question, and a 25-second
scanner cannot see inside one interval. The other 12,479 rows priced 1–4¢ *over* $1 combined.

## Settlement divergence (the risk the two-leg trade actually carries)

A pair is only an arbitrage if both venues settle on the same fact. Measured on settled history:

| series | divergent settlements | 95% upper bound (rule of three) |
|---|---|---|
| MLB games | 0 / 807 | 0.4% |
| WTA tennis | 0 / 540 | 0.6% |
| ATP tennis | 1 / 453 | — (one observed: 0.2%) |
| College football | 0 / 330 | 0.9% |
| WNBA | 0 / 138 | 2.2% |
| NFL | 0 / 77 | 3.9% |

Every settled series in the sample is listed. NFL, the series behind the two in-play crosses above, has the
smallest sample and therefore the weakest bound: nothing observed, but the data cannot yet rule out a
divergence rate below about 4%.

The first live pair to retire settled identically on both venues, about 25 minutes apart.

## Method notes

- Fees per venue from each venue's own schedule (see the [fee sheet](fees.md)); depth walked level by
  level; a book too thin for the minimum size prices as *none*, never as a partial.
- Error rows are neutral to persistence windows; the scan interval is derived from the data, not assumed.
- Numbers on this page are the sealed scores. The board republishes live; live counts drift as pairs retire.
