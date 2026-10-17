# Number audit, 2026-10-17

Scope: every figure on `index.md`, `track-record.md`, `fees.md`, `engineering.md` and `board.html`, checked
against what the repository holds. **The repository holds no generator, kernel, scanner or raw data.** It
holds only the published pages: 50 commits, each a `board.html` snapshot (2026-10-16 15:08 to 2026-10-17
02:30). So a figure is *checkable* only when it can be recomputed from other figures on the pages or
from the 50 committed board snapshots. Everything else is listed as UNVERIFIABLE, grouped.

Reproduce: `python3 _audit/board_audit.py --history` and `python3 -m unittest discover -s _audit -v`
(stdlib only; `_audit/` is underscore-prefixed, so Jekyll does not publish it).

## Code bugs

There are none I can fix in this repository. The only executable code here is the ~20 lines of sort,
filter and clock JavaScript in `board.html`. I read it and found no defect that changes a displayed
number. Every WRONG item below comes either from the generator that writes `board.html`, which is not
in the repo, or from prose. Following "failing test first", the tests in `BoardAgainstItsOwnLabels`
**fail today** and are written as the spec for that generator. I did not edit `board.html` or any
other published page: those are publications, and `board.html` is overwritten about every 14 minutes.

## WRONG

| # | where | claim | evidence (reproduced) | right value / proposed wording |
|---|---|---|---|---|
| W1 | board, reasoning on pairs 01–03; `$ edge` column tooltip | "500 contracts (the most that stays under $1 walking both books)" / "largest q still under $1" | The best level alone holds 1,159 / 2,157 / 4,961 contracts, and 500 is the cap that the fill-record text states ("capped at 500"). `test_size_label_is_not_the_cap` | "500 contracts (the instrument's size cap; the best level alone holds 1,159 under $1)" |
| W2 | board, paper fill record | "Counts accrue over every row recorded since 2026-09-27" | Across the 49 consecutive snapshot pairs, decisions fell 27 times (1,483 → 1,360 overall), rows replayed fell 22 times, contracts attempted fell 19 times, and net $ fell 20 times ($3,486.25 → $3,310.99). Separately, 12,496 scans × the page's own ~29 s is 4.2 days of data, not the 20.3 days since 2026-09-27. Counts that accrue cannot fall. `test_counts_accrue`, `test_record_covers_its_since_date` | The correct total cannot be recovered from the repo. Proposed: "Counts cover the rows currently held for the 16 pairs on the board (about the last 12,500 scans), so they can fall as old rows leave." |
| W3 | board, short-dated fill line vs track record | "Short-dated (settle ≤ 14 d) — no rows", under "every row since 2026-09-27" | Experiment 2 recorded 12,481 short-dated rows on 2026-09-27. | The same fix as W2: the record covers current pairs only, and should say so. |
| W4 | board, header strip | "Scans 12496 · 199929 rows" presented as a running count | The count is identical in all 50 snapshots over 11.4 h (about 1,400 new scans expected at ~29 s). Over the same fixed 199,929 rows, the total sub-$1 count (summed over pairs) moved from 68,705 to 67,778, and a fixed set of rows cannot change its sub-$1 count. So these are fixed-size window figures, not totals. Whether that comes from a rolling window, a capped store, or something else is UNVERIFIABLE. `test_scan_counter_advances`, `test_fixed_rows_keep_their_sub_dollar_count` | "Last 12,496 scans · 199,929 rows" (with the same caveat on each row's `Sub-$1 / rows`) |
| W5 | index.md | "republished every 10 minutes" | The median gap between the 49 commits is 13.9 min (min 13.2, max 15.3). `test_republished_every_ten_minutes` | "republished about every 15 minutes" |
| W6 | board, reasoning on NO EDGE rows 07, 10, 12 | "a size floor around q≥5" | The same rule the board applies to rows 01–06 (smallest q at which the unrounded Kalshi fee reaches 1¢), applied to each row's own price, gives about 143 (pair 07, NO at 0.999), 6 (pair 10, NO at 0.973) and 8 (pair 12, YES at 0.020). These rows appear to fall back to q_min. `test_size_floor_text` | Print the computed floor on every row, or drop the phrase where net ≤ 0. |
| W7 | fees.md | "a 0.2¢ gap needs about six contracts to break even" | With the 1¢ minimum fee, net is 0.2·q − 1¢: exactly 0 at q = 5 and first positive at q = 6. The sentence before it ("at five contracts a gap must *exceed* 0.2¢") is right. `test_point_two_cent_gap_breaks_even_at_five` | "a 0.2¢ gap breaks even at five contracts and first clears at six" |
| W8 | engineering.md | "observed median gap between scans is about 25 s, which is the cadence every page here means by 'one scan'" | The board's own "median gap between books" reads 26–29 s across the 50 snapshots, and its header reads "~29 s" today. | "about 25–30 s (the board prints the current median)" |
| W9 | track-record.md, NFL | "the data cannot yet rule out a divergence rate below about 4%" | The rule of three gives an upper bound: 3/77 = 3.9%. A zero-in-77 result cannot rule out rates *up to* about 4%. As written, the sentence says the opposite. | "cannot yet rule out a divergence rate as high as about 4%" |

## MATCHES

**board.html: all 50 snapshots × 16 rows = 800 row-checks, zero failures** (`test_every_row_recomputes`):
- gross gap = 100·(1 − P_K − P_P), allowing for the 3-dp price display
- Kalshi vig = ceil(0.07·M·q·P(1−P)) to the cent, per order, at the priced size (500, 20 or q_min 5)
- Polymarket vig = rate·p(1−p)
- net = gross − both vigs
- $ edge = net·q/100
- break-even P(diverge) = net/50
- Sub-$1 % = count / rows seen
- each verdict, by the footer's test order

**board.html, page-level checks (all 50 snapshots):**
- The strip counts (0 live / 3 carry / 3 dust / 0 thin / 10 no edge) equal the row verdicts.
- 199,929 rows = Σ rows seen (7 × 12,495 + 9 × 12,496).
- The depth legend's "max 20165" equals the largest depth.
- Today's fill record: 91% = 500,491 / 552,955 (90.5%); 0.67% = $3,310.99 / $497,180 (0.666%).
- Attempted contracts ≤ 500 × decisions; "11 of 16 pairs" is ≤ the 11 pairs with any sub-$1 rows.
- The footer stamp 02:30:03 is within 1 s of `data-generated` (02:30:04 CDT).

**index.md / track-record.md:**
- 976/3,863 = 25.3%; 1,219/3,863 = 31.6%; 2/12,481 = 0.016%; 976 − 9 = 967; 12,481 − 2 = 12,479.
- Row counts fit inside scans × pairs (3,870 ≤ 3,904; 12,546 ≤ 13,604).
- Best carry: 2.27¢ × 500 = $11.35 on $488.65 for 773 d = 1.10%/yr.
- $4.94 for five = 1.2¢/ct; $4.99 for five = 0.2¢/ct.
- Rule of three: 3/807 = 0.4%, 3/540 = 0.6%, 3/330 = 0.9%, 3/138 = 2.2%, 3/77 = 3.9%; ATP 1/453 = 0.2%.
- "four of six held … two refuted".

**fees.md:**
- Polymarket US max 0.0695 × 100 × 0.25 = $1.7375 → $1.74.
- Rounding table for a 0.3¢ fee: 1¢ / 0.3¢ / 0¢.
- At 5 contracts the 1¢ minimum equals 0.2¢/ct.

**engineering.md:**
- "35 certified" = 16 long-dated + 19 short-dated.
- Seven parameters are named, and seven are listed.

## Ambiguous wording (no single right value)

- **Break-even P(diverge).** The board computes net/50. If "a −50¢/contract loss" means the whole
  outcome when settlement diverges, the formula is net/(net+50). For pair 01 that is 2.24% against the
  2.29% shown. Either state "net/50 (the loss is in addition to the forgone edge)" or switch formulas.
- **"legged 1,260".** No unit is given. At `c8c2514` it read 1,760 while decisions read 1,432, so it
  cannot be a count of decisions. Say "contracts legged" if that is what it counts.
- **Decisions vs their definition.** Pairs 01–03 are net-positive at q_min in all 50 snapshots and
  sub-$1 on 100% of about 12,495 rows each. The stated definition ("any recorded observation where …")
  would then give at least ~37,000 decisions, against the 1,360 shown, so some de-duplication or holding
  rule must apply. The text should state it.
- **%/yr is rounded to whole percent.** Positive CARRY-NEGATIVE rows read "about +0%/yr", and the days
  locked are withheld. Show one decimal place.
- **Experiment 1, internally inconsistent.** The track record says "under $1 on every scan for five
  hours" over 244 scans, which is about 74 s per scan, not the ~25 s "one scan" defined in
  engineering.md. It also says "the 11 windows are those four permanent gaps cut by the seven
  fetch-error scans", while the method notes say "Error rows are neutral to persistence windows". Both
  cannot describe the same scoring. The private files would settle it.
- **index.md "gone within 25 seconds".** The track record itself says ~25 s is the scan cadence, a
  resolution floor, not a measured lifetime. Proposed: "gone by the next scan, about 25 s later".

## UNVERIFIABLE (nothing in the repo to recompute from)

- **Kernel and performance:** the Lean kernel and its theorems; 273–423 ns, 1.39 µs, 68 µs; TLA+
  12 / 1,701 states; the 64-byte block; latencies (160–220 ms, 70 ms, 270–350 ms, 1.6 s); the 20 s
  scheduler; "33 live".
- **Experiment raw data:** scan, row and error counts for experiments 1 and 2; the 11 windows (median
  9, 6/11); depth ≥ 500; all experiment-3 figures (log-losses, CI, 42,316 rows / 696 pairs, 48 / 54
  pairs, bin gaps 0.197 / 0.174); the settlement-divergence counts; the SHA-256 prefixes (the files are
  private).
- **Venue facts in fees.md:** fee formulas and rates, M, maker fees, rate-limit tiers, ticks, dates.
  These are bound to venue documents, not to the repo.
- **External claims:** the four paid products, the bot review, the prior-work citations and their
  figures.

## What changed

Only `_audit/` was added: `board_audit.py` (parser plus recomputation), `test_board_audit.py` (16
tests: 6 pass, 10 fail as described above), and this report. No published page, `_config.yml`, Pages
setting or `main` was touched. The work is on branch `claude/number-audit-cp6ol4`: the session's
designated branch, which carries a harness suffix on the requested name `claude/number-audit`.
