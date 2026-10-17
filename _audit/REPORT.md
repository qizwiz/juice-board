# Number audit — 2026-10-17

Scope: every number and checkable claim on `index.md`, `track-record.md`, `fees.md`, `engineering.md` and
`board.html` (snapshot generated 2026-10-17 03:04:01), checked against what this repository holds.

**What the repo holds.** The five published pages, plus 50 committed snapshots of `board.html`
(2026-10-16 15:36 → 2026-10-17 03:04, about 11.5 h). There is **no generator, no raw scan data, and no
Lean, TLA+ or Python source**. A claim counts as verifiable only if it can be recomputed from figures on the
pages themselves or from the snapshot history.

Reproduce everything: `python3 -m unittest discover -s _audit -v` (standard library only). Tests marked
`expectedFailure` are the failing tests behind the WRONG findings. They fail today. If the upstream
generator is fixed, unittest reports an *unexpected success*, which fails the suite.

## WRONG

| # | claim (page) | what the repo shows | evidence |
|---|---|---|---|
| W1 | "Counts accrue over every row recorded since 2026-09-27" (board, paper fill record) | It is a **rolling window of about 200,000 rows**, not a running total. Over the 50 snapshots, rows replayed moved between 199,835 and 199,889. Decisions **fell** from 1,493 to 1,357, contracts filled from 517,783 to 500,491, and net from $3,457.19 to $3,310.99. "Legged" stayed at 1,260 throughout. | `test_paper_record_accrues_every_row_since_sept_27` fails: 1483 < 1493 at the second snapshot |
| W2 | "Scans 12496 · 199929 rows" and "Sub-$1 / rows" (board) | Both read as running totals but are the same window. Scans = 12,496 on all 50 snapshots, even though prices and depth changed in every one. Per-pair numerators **go down** while their denominators stay frozen at 12,495/12,496 (e.g. pair-05 went from 10,574/12,495 to 10,545/12,495). 199,929 / 16 pairs = 12,495.6 rows per pair, so the denominators come from the row window. | `test_scans_and_sub_dollar_counts_are_cumulative` fails: 12496 not > 12496 |
| W3 | `%/yr` column: "+0.00" on pairs 02–06, "+1.00" on pair 01 (board) | `data-ann` only ever holds −1, 0 or +1 (on all 50 snapshots), so the value is rounded to a whole percent upstream and then printed with two decimals. Pair-02 earns +1.10¢ net on a 98.9¢ outlay. Even if it were locked until 2045, the latest settlement on the track-record page, that comes to ≥ 0.058 %/yr, not 0.00. **Right value: UNVERIFIABLE**, because `Locked (d)` is blank on every row. The verdicts are not affected: all ≤ 1.2 %/yr is still below 4 %. | `test_annualised_carry_is_not_rounded_to_whole_percent` fails: pair-02 ann 0.0 |
| W4 | `$ edge on screen` tooltip: "…the executable size … when the scan carries it, else the quoted depth" (board) | When there is no executable size, the edge is priced at **q_min = 5**, not at the quoted depth. Pair-07: depth 26, edge −0.0102 = −0.204 × 5 / 100 (using depth it would be −0.053). Pair-11: depth 20,165, edge −0.0293 = −0.5864 × 5 / 100. The same holds for all 10 NO EDGE rows. | `test_dollar_edge_tooltip_quoted_depth_fallback` fails at pair-07 |
| W5 | "republished every 10 minutes" (index) | The gaps between snapshot commits have a **median of 13.9 min** (range 13.2–17.2 min, 49 gaps). | `test_republished_every_ten_minutes` fails: median 13.9 |

## Inconsistent across pages (wording fix needed; the underlying number is UNVERIFIABLE)

| # | claims | issue |
|---|---|---|
| I1 | engineering: median scan gap "about 25 s", "the cadence every page here means by 'one scan'"; track record and index: "about 25 seconds". Board: "read every ~35 s", "median gap between books is ~35 s". | The board computes its own figure, and across the 50 snapshots it read 26–35 s (median 27). Today it reads 35. No page agrees with "25 s" over the last 11.5 h. |
| I2 | Track record, exp. 1: four pairs under $1 "on every scan **for five hours**" at G1 = 244 scans | 244 × 25 s ≈ 1.7 h. Five hours would need about 74 s per scan. Either the duration or the cadence is wrong for that run. |
| I3 | Track record: "the '11 windows' are those four permanent gaps **cut by the seven fetch-error scans**" vs Method notes: "Error rows are **neutral** to persistence windows" | These contradict each other directly. If errors were neutral, the four permanent gaps would make four windows. Nine flicker rows would then have to supply seven windows, and "6/11 lasted ≥ 3 scans" could not hold. So the "neutral" rule cannot produce the reported G3 numbers. Either the method note or the scoring is misdescribed. |
| I4 | Index/track record: 967 rows from "four pairs that priced under $1 on every scan" | 967 / 4 = 241.75. The four pairs had unequal row counts, so "every scan" must mean every *clean* row of each pair. That is fine, but worth one clause. |

## Wording fixes proposed (published pages not edited)

1. **board, paper fill record (W1):** replace "Counts accrue over every row recorded since 2026-09-27" with
   "Counts cover the most recent ~200,000 recorded rows (a rolling window), so they can fall as old rows age out."
2. **board strip (W2):** "Scans 12496 · 199929 rows" → "Window: last 12,496 scans · 199,929 rows". Change the
   `Sub-$1 / rows` tooltip to say "within the window".
3. **board `%/yr` (W3):** generator fix: emit `ann` unrounded (e.g. `f"{ann:+.2f}"` on the raw value), or
   print whole percents ("+1", "0") so the column does not claim two decimals. The hover's "about +0%/yr" is
   honest as written.
4. **board `$ edge` tooltip (W4):** "…else the minimum order size (5 contracts)".
5. **index (W5):** "republished about every 15 minutes".
6. **engineering/track record/board (I1):** give one cadence and say when it was measured, e.g. "about 25 s
   on 2026-09-27; the board prints the current median (26–35 s on 2026-10-16/17)".
7. **track record (I2, I3):** check the five-hours figure against the scan log. Then reconcile the method note
   with what the G3 scorer actually did. If error scans cut windows, say so in Method notes.
8. **track record, NFL:** "the data cannot yet rule out a divergence rate **below** about 4%" reads backwards.
   Write: "cannot yet rule out a divergence rate **as high as** about 4%".
9. **fees, size floor:** "a 0.2¢ gap needs about six contracts to break even" holds only while the Kalshi fee
   sits at its 1¢ minimum (at six contracts that means P(1−P) ≤ 0.024, i.e. prices within ~2.4¢ of 0 or $1).
   It also ignores the Polymarket leg. At P = 0.50, six contracts pay 11¢ (1.83¢ each). Add "at prices near
   0 or $1, before the Polymarket fee".
10. **track record G2:** 1,219 rows under $1 at ≥ $5 depth vs 976 at minimum size looks inverted, since a
    bigger size usually costs more. It is plausible because Kalshi's per-order ceiling amortises over more
    contracts. One sentence saying so would stop readers from reading it as an error.
11. **board "Last scan … ago":** the JS counts from `data-generated` (page build time), not from a scan time.
    Either label it "Built … ago" or emit the last scan's timestamp. Proposed patch for the generator template:
    `<body data-generated="{built}" data-last-scan="{last_scan_ts}">` and `const gen=Number(document.body.dataset.lastScan)*1000;`.
12. **board hover text:** leg prices are printed to 3 dp but are depth-walked averages. For example, pair-04
    "0.997 + 0.002" sums to 0.999 while the stated gross is 0.9986. Print 4 dp or say "average".

## MATCHES

| claim | recomputation |
|---|---|
| Board, every row: net = gross − K vig − P vig | 16/16 rows, to 4 dp |
| Board, every row: K vig = ceil(0.07·q·P(1−P)) / q | 16/16 at q = executable size (500 or 20) or q_min 5, within the 3-dp display of P |
| Board, every row: P vig = rate·p(1−p) | 16/16 (rates 0.04 or 0) |
| Board: $ edge = net × priced size; break-even P(diverge) = net / 50¢ | 16/16 |
| Board: Sub-$1 % = numerator / denominator | 16/16 |
| Board: verdicts follow the footer's ordered rules (NO EDGE → DUST < $1 → CARRY < 4 %) | 16/16 |
| Board strip: 0 live / 3 carry / 3 dust / 0 thin / 10 no edge | matches rows |
| Board: 199,929 rows = Σ per-pair denominators | on all 50 snapshots |
| Board: depth legend max 20,165 | = max depth (pair-11) |
| Board paper record: "11 of 16 pairs" | = pairs with a non-zero sub-$1 count |
| Board paper record: 91 % filled; 0.67 % in total; ≤ 500 contracts per decision | 500,491 / 551,455 = 90.8 %; 3,310.99 / 497,180 = 0.666 %; 551,455 ≤ 1,357 × 500 |
| Board: `data-generated` vs footer timestamp | 03:04:02 vs 03:04:01 CDT |
| Index/track record: 25.3 %, 31.6 %, 967 + 9 = 976 | 976/3,863 = 25.27 %; 1,219/3,863 = 31.56 % |
| Exp. 1 best carry: 2.27¢, ~$11 on ~$490, 773 d → 1.1 %/yr | 2.27 × 500 = $11.35; 11.35/490 × 365/773 = 1.09 % |
| Exp. 2: 2/12,481 = 0.016 %; 12,479 others; 1.2¢ and 0.2¢ per contract | 0.0160 %; (5 − 4.94)/5; (5 − 4.99)/5 |
| Settlement bounds 0.4 / 0.6 / 0.9 / 2.2 / 3.9 %; ATP 0.2 % | 3/807, 3/540, 3/330, 3/138, 3/77; 1/453 |
| Exp. 3: 4 + 2 = 6 predictions; 48- and 54-pair blocks ≥ 40 | arithmetic |
| Fees: Polymarket US max $1.74 / 100 at p = 0.50 | 0.0695 × 100 × 0.25 = 1.7375 |
| Fees: 1¢ / 5 = 0.2¢ floor; 0.7¢ clears at five; rounding table 1¢ / 0.3¢ / 0¢ | arithmetic (see wording fix 9 for the condition) |

## UNVERIFIABLE (no source in the repo)

- Experiments' underlying counts: 244/716 scans, 16/19 pairs, 3,863/12,481 clean rows, 7/65 fetch errors,
  11 windows, median 9, 6/11; "≥ 500 contracts of depth"; 9 of 238 scans; "1–4¢ over $1"; depth 210/500.
- SHA-256 prefixes (files private); pre-registration and scoring dates.
- Experiment 3: 0.5162 / 0.5170 / 0.5654 log-loss, 42,316 rows / 696 pairs, +0.0010 [+0.0001, +0.0020],
  +0.025 / −0.024, bin gaps 0.197 / 0.174.
- Settlement sample sizes (807, 540, 453, 330, 138, 77) and "25 minutes apart".
- Engineering: 273–423 ns, 1.39 µs, 68 µs, 7 parameters / 64-byte block, TLA+ 12 and 1,701 states, latency
  160–220 / 70–145 / 70 / 270–350 ms, 1.6 s scan, 20 s scheduler, 35 certified / 33 live.
- All venue facts on the fee sheet (formulas, multipliers, maker fees, rates per sport, ticks, min size,
  rate-limit tiers, US blocking, Θ changes, rebate tiers). The board's live data agrees with the Kalshi
  formula and the Polymarket 0.04 rate, and two board pairs carry rate 0.
- Index: four paid products read 2026-09-27; the open-source bot review; the literature (Rothschild &
  Pennock 2014; arXiv 2601.01706, 2608.00666, 2605.00864). These are outside the repo and were not fetched.
- Board size-floor hints ("q≥18", "q≥42", …): they track 1 / (0.07·P(1−P)), but pairs 05/06 truncate and
  pair 04 rounds up. Without the exact prices or the code, it cannot be settled.

## What changed

- Added `_audit/board.py` (parses `board.html` and its git history), `_audit/test_audit.py` (26 tests:
  21 pass as MATCHES, 5 expected failures = W1–W5) and this report. They sit under `_audit/` so Jekyll does
  not publish them even if merged. No published page, `_config.yml`, or deploy setting was touched.
- **No code bug was fixed, because no code that produces these numbers is in this repository.** W1–W4 live
  in the upstream generator (arb-watch) and W5 in the publishing schedule. The failing tests are written so
  that they can be pointed at a corrected `board.html` without changes.
