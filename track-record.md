# Track record

All three experiments were **pre-registered**: hypotheses, gates and the scoring rule were written down before
scoring, and all three have now been **scored** against those gates. The first two were sealed before their first
observation; the third was sealed before its evaluation but after its held-out block had been looked at, and says so. The files are private for now
(they name the pairs); their SHA-256 digests are published so the text can be checked later against what
exists today. Each digest covers the file as it stands, pre-registration plus its scored result section.

| experiment | pre-registered | scored | sha256 of the file (prefix) |
|---|---|---|---|
| 1 · long-dated pairs (settle 2028 or later; two close in 2045) | 2026-09-27 | 2026-09-27, at 244 scans | `5599869f2a665e81` |
| 2 · short-dated pairs (settle ≤ 14 days) | 2026-09-27 | 2026-09-27, at 716 scans | `cb5df22999b47ea9` |
| 3 · forecaster: per-series recalibration of a venue mid | 2026-09-28 | 2026-09-28, one evaluation | `83b6efd9885c2a9b` |

Experiment 2's scoring gate (100 scans) fell hours before anyone scored it; the result section says so.
Experiment 3's pre-registration discloses that its idea came from looking at the held-out block's reliability
table, so that block was held out from training but not blind to the author; its result is reported that way.

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

## Experiment 3 — can a venue's own mid be recalibrated?

**Question.** The first forecaster pass (2026-09-27) found nothing trained on the two venues' prices beat the
better venue's mid on held-out log-loss (best venue 0.5162, logistic blend 0.5170, trees 0.5654). The cheapest
remaining candidate: is the mid *miscalibrated* in a way that is stable within a series, so that a monotone
recalibration per series (a two-parameter Platt map or a 40-bin isotonic step), fit on the training block,
beats the raw mid?

**Grounded on training data only** before the run: a global recalibration made the validation block worse; one
series flipped the sign of its bias between blocks; only the two tennis series both carried the same bias in
both blocks *and* improved on transfer from one block to the other. So the pre-registration narrowed the claim to tennis, kept the raw mid as a candidate in the selection,
required at least 40 pairs in both blocks, and fixed the gate and six predictions with credences.

**Result, one evaluation on 42,316 held-out rows / 696 pairs:** the recalibrated mid is **significantly worse**
than the raw mid, +0.0010 log-loss, 95% CI [+0.0001, +0.0020] by cluster bootstrap over pairs. The series that
carried the hypothesis gained 0.025 on the 48-pair validation block and then **lost 0.024 on the 54-pair test
block**. Four of six predictions held (the selection outcome, the gate failing, the secondary candidates losing);
the two refuted were the per-series log-loss gain and the calibration check: on tennis rows the recalibrated
mid's reliability curve is *worse* than the raw mid's (largest bin gap 0.197 against 0.174). Second forecaster
pass, same conclusion as the first: at hourly granularity the better venue's mid is not improved by anything
fit to its own history.

**What changes because of it.** A forward ledger is now open: every later evaluation scores only pairs that
settled *after the last settlement in the examined block* (2026-09-27), with the weights frozen, so the next
number is one nobody has seen in advance.

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

## Prior work (added 2026-09-28 after an independent literature check)

None of this is the first measurement of cross-venue prediction-market mispricing, and the site should say so.

- **Rothschild & Pennock (2014)**, *Algorithmic Finance* 3: real-money Intrade/Betfair pairs in 2012 showed
  executable net gaps of 1–5% after costs, and a field trial of $3,686 returned 6.38% over three months
  including transaction costs. There, the **persistent** gap was the profitable one, the opposite of the reading
  above. Both can hold: different venues, era and access structure (Betfair barred US users).
- **Gebele & Matthes (2026)**, arXiv 2601.01706: across ten venues and 102,275 events, semantically equivalent
  markets show persistent execution-aware deviations of 2–4% on average. Flat per-venue fee model, not per-order.
- **Gebele, Mutzel & Matthes (2026)**, arXiv 2608.00666: intra-Polymarket, prices arbitrage at depth-walked,
  fee-adjusted executable cost and separates payoff-space from protocol-executable no-arbitrage. A precedent for
  the executable-size pricing used here.
- **Cheng, Yang & Zou (2026)**, arXiv 2605.00864: 75 million Polymarket NBA book snapshots, seven executable
  in-game episodes with a median life of 3.6 s, which is that study's polling floor. Likewise, the "about 25
  seconds" above is this instrument's scan cadence, a resolution floor, not a measured lifetime.

The same review examined four open-source bots on 2026-09-28: speedyhughes/kalshi-poly-arb (the one cross-venue
bot; assumes Polymarket charges no fee, detects at top-of-book only, publishes no result); profintegra/polymarket-arbitrage
and MrFadiAi/Polymarket-bot (intra-Polymarket YES+NO; no fee computation; no result, fill count or denominator
published); and kachence/polymm (intra-Polymarket maker; a stated "after fees" threshold with no fee computation
in the code; its author-reported profit figures did not survive the review's verification). A fifth repository,
ImMike/polymarket-arbitrage, self-described as cross-venue, appears only in the review's source list: no finding,
caveat or verification vote concerns it, so it is unmeasured here and not counted.

What this site adds to that record is narrower than "first": three separately bound fee models across three
venues, pricing at the executable size, sealed pre-registrations scored as written, and a public denominator.

## Method notes

- Fees per venue from each venue's own schedule (see the [fee sheet](fees.md)); depth walked level by
  level; a book too thin for the minimum size prices as *none*, never as a partial.
- Error rows are neutral to persistence windows; the scan interval is derived from the data, not assumed.
- Numbers on this page are the sealed scores. The board republishes live; live counts drift as pairs retire.
