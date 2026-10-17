"""Recompute the numbers published on this site from what the repo holds.

Run from the repo root:  python3 -m unittest discover -s _audit -v

Ordinary tests are claims that MATCH. Tests marked @expectedFailure are claims the
repo's own data shows are WRONG; they fail today, and unittest reports an
"unexpected success" (a suite failure) once the upstream generator is fixed, so
they cannot silently go stale. See _audit/REPORT.md for the finding behind each.
"""
import math
import statistics
import unittest
from datetime import datetime, timedelta, timezone

import board

B = board.load()
ROWS = B["rows"]
Q_MIN = 5
DIVERGENCE_LOSS_C = 50  # board footer: "assumes a −50¢/contract loss"


def kalshi_vig_c(price, q):
    """Kalshi taker fee per contract in cents: ceil(0.07·q·P(1−P)) to the cent, spread over q."""
    fee_cents = 0.07 * q * price * (1 - price) * 100
    return math.ceil(round(fee_cents, 9)) / q


def poly_vig_c(price, rate):
    return 100 * rate * price * (1 - price)


def near(prices, half_tick=0.0005, steps=50):
    """Prices the board's 3-decimal display could be rounding (it prints the depth-walked average)."""
    return [prices + half_tick * (i / steps * 2 - 1) for i in range(steps + 1)]


def size(r):
    return r["q"] or Q_MIN


class RowArithmetic(unittest.TestCase):
    """Every per-row figure on board.html, recomputed from the row's own inputs."""

    def test_net_is_gross_minus_both_vigs(self):
        for r in ROWS:
            self.assertAlmostEqual(r["net"], r["gross"] - r["kvig"] - r["pvig"], places=3, msg=r["pair"])

    def test_gross_matches_leg_prices_to_display_precision(self):
        for r in ROWS:
            self.assertLessEqual(abs(r["gross"] - 100 * (1 - r["k_price"] - r["p_price"])), 0.1, r["pair"])

    def test_kalshi_vig_is_ceiling_fee_at_priced_size(self):
        for r in ROWS:
            ok = any(abs(kalshi_vig_c(p, size(r)) - r["kvig"]) < 1e-6 for p in near(r["k_price"]))
            self.assertTrue(ok, f'{r["pair"]}: kvig {r["kvig"]} at q={size(r)}, P≈{r["k_price"]}')

    def test_polymarket_vig_is_rate_times_p_one_minus_p(self):
        for r in ROWS:
            ok = any(abs(poly_vig_c(p, r["rate"]) - r["pvig"]) < 6e-5 for p in near(r["p_price"]))
            self.assertTrue(ok, r["pair"])

    def test_dollar_edge_is_net_times_priced_size(self):
        for r in ROWS:
            self.assertAlmostEqual(r["edge"], r["net"] * size(r) / 100, places=3, msg=r["pair"])

    def test_break_even_divergence_is_net_over_assumed_loss(self):
        for r in ROWS:
            if r["net"] > 0:
                self.assertAlmostEqual(r["pstar"], r["net"] / DIVERGENCE_LOSS_C, places=5, msg=r["pair"])
            else:
                self.assertIsNone(r["pstar"], r["pair"])

    def test_sub_dollar_share_is_numerator_over_denominator(self):
        for r in ROWS:
            self.assertAlmostEqual(r["persist"], 100 * r["sub"] / r["seen"], places=2, msg=r["pair"])

    def test_verdicts_follow_the_footer_rules(self):
        for r in ROWS:
            if r["net"] <= 0:
                want = "NO EDGE"
            elif r["edge"] < 1:
                want = "DUST"
            elif r["ann"] < 4:
                want = "CARRY-NEGATIVE"
            else:
                want = "LIVE EDGE"
            self.assertEqual(r["verdict"], want, r["pair"])

    @unittest.expectedFailure
    def test_dollar_edge_tooltip_quoted_depth_fallback(self):
        # Column tooltip: "... the executable size ... when the scan carries it, else the quoted depth".
        # Rows without an executable size are priced at q_min = 5, not at the quoted depth
        # (pair-11: depth 20,165, edge −0.0293 = −0.5864 × 5 / 100).
        for r in ROWS:
            if r["q"] is None:
                self.assertAlmostEqual(r["edge"], r["net"] * r["depth"] / 100, places=3, msg=r["pair"])

    @unittest.expectedFailure
    def test_annualised_carry_is_not_rounded_to_whole_percent(self):
        # Long-dated pairs settle no later than 2045 (track record). A positive net edge locked
        # for at most that long cannot annualise to exactly 0.0000 %/yr, yet the board prints
        # data-ann="0.0000" ("+0.00") for pair-02..06 and only ever emits −1, 0 or +1.
        horizon_years = (datetime(2046, 1, 1) - datetime(2026, 10, 17)).days / 365
        for r in ROWS:
            if r["net"] > 0:
                outlay = 100 - r["gross"] + r["kvig"] + r["pvig"]
                floor = 100 * (r["net"] / outlay) / horizon_years
                self.assertGreater(r["ann"], floor / 2, r["pair"])
        self.assertGreater(len({r["ann"] for r in ROWS} - {-1.0, 0.0, 1.0}), 0)


class BoardTotals(unittest.TestCase):

    def test_verdict_strip_counts_rows(self):
        for label, verdict in [("Live edge", "LIVE EDGE"), ("Carry-negative", "CARRY-NEGATIVE"),
                               ("Dust", "DUST"), ("Thin", "THIN"), ("No edge", "NO EDGE")]:
            self.assertEqual(B["strip"][label], sum(r["verdict"] == verdict for r in ROWS), label)

    def test_row_total_is_sum_of_per_pair_denominators(self):
        self.assertEqual(B["nrows"], sum(r["seen"] for r in ROWS))

    def test_depth_legend_max_is_max_depth(self):
        self.assertEqual(B["depth_legend_max"], max(r["depth"] for r in ROWS))

    def test_paper_record_internal_arithmetic(self):
        p = B["paper"]
        self.assertEqual(p["pairs_with_decisions"], sum(r["sub"] > 0 for r in ROWS))
        self.assertEqual(p["pairs_total"], len(ROWS))
        self.assertEqual(p["filled_pct"], round(100 * p["contracts_filled"] / p["contracts_wanted"]))
        self.assertAlmostEqual(p["total_pct"], 100 * p["net"] / p["locked"], places=2)
        self.assertLessEqual(p["contracts_wanted"], 500 * p["decisions"])  # "capped at 500 contracts"

    def test_generated_stamp_matches_footer(self):
        local = datetime.fromtimestamp(B["generated"], timezone(timedelta(hours=-5)))  # CDT
        footer = datetime.strptime(B["footer_generated"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=local.tzinfo)
        self.assertLessEqual(abs((local - footer).total_seconds()), 2)


class SnapshotHistory(unittest.TestCase):
    """Claims about how the board behaves over time, checked against its committed snapshots."""

    @classmethod
    def setUpClass(cls):
        try:
            cls.snaps = board.history()
        except Exception as e:  # shallow clone or no git
            raise unittest.SkipTest(f"git history unavailable: {e}")
        if len(cls.snaps) < 3:
            raise unittest.SkipTest("need several snapshots")

    def test_snapshots_are_internally_consistent(self):
        for _, s in self.snaps:
            self.assertEqual(s["nrows"], sum(r["seen"] for r in s["rows"]))

    @unittest.expectedFailure
    def test_republished_every_ten_minutes(self):
        # index.md: "the live-ish snapshot (republished every 10 minutes)".
        gaps = [(b[1]["generated"] - a[1]["generated"]) / 60 for a, b in zip(self.snaps, self.snaps[1:])]
        self.assertLessEqual(abs(statistics.median(gaps) - 10), 2, f"median gap {statistics.median(gaps):.1f} min")

    @unittest.expectedFailure
    def test_paper_record_accrues_every_row_since_sept_27(self):
        # board.html: "Counts accrue over every row recorded since 2026-09-27". A cumulative
        # count never shrinks; across the snapshots decisions fell 1,493 → 1,357 and contracts
        # 517,783 → 500,491, while rows replayed hovered just under 200,000.
        for (_, a), (_, b) in zip(self.snaps, self.snaps[1:]):
            for k in ("replayed", "decisions", "contracts_wanted", "contracts_filled"):
                self.assertGreaterEqual(b["paper"][k], a["paper"][k], k)

    @unittest.expectedFailure
    def test_scans_and_sub_dollar_counts_are_cumulative(self):
        # The strip says "Scans 12496" on every snapshot over ~11.5 h while prices and depth
        # changed, and per-pair "Sub-$1 / rows" numerators went down with frozen denominators:
        # a rolling ~200k-row window, presented as a running total.
        first, last = self.snaps[0][1], self.snaps[-1][1]
        self.assertGreater(last["scans"], first["scans"])
        for (_, a), (_, b) in zip(self.snaps, self.snaps[1:]):
            prev = {r["pair"]: r["sub"] for r in a["rows"]}
            for r in b["rows"]:
                self.assertGreaterEqual(r["sub"], prev.get(r["pair"], 0), r["pair"])


class PublishedPageArithmetic(unittest.TestCase):
    """Figures in the Markdown pages that can be recomputed from figures stated alongside them."""

    def test_experiment_1_rates(self):
        self.assertEqual(round(100 * 976 / 3863, 1), 25.3)
        self.assertEqual(round(100 * 1219 / 3863, 1), 31.6)
        self.assertEqual(976 - 9, 967)

    def test_experiment_1_best_carry(self):
        dollars = 2.27 * 500 / 100  # "about $11"
        self.assertAlmostEqual(dollars, 11, delta=0.5)
        self.assertEqual(round(100 * dollars / 490 * 365 / 773, 1), 1.1)

    def test_experiment_2_rates_and_crosses(self):
        self.assertEqual(round(100 * 2 / 12481, 3), 0.016)
        self.assertEqual(12481 - 2, 12479)
        self.assertAlmostEqual((5 - 4.94) / 5 * 100, 1.2)
        self.assertAlmostEqual((5 - 4.99) / 5 * 100, 0.2)

    def test_rule_of_three_bounds(self):
        for n, shown in [(807, 0.4), (540, 0.6), (330, 0.9), (138, 2.2), (77, 3.9)]:
            self.assertEqual(round(300 / n, 1), shown, n)
        self.assertEqual(round(100 / 453, 1), 0.2)

    def test_experiment_3_prediction_tally(self):
        self.assertEqual(4 + 2, 6)
        self.assertTrue(48 >= 40 and 54 >= 40)  # "required at least 40 pairs in both blocks"

    def test_fee_sheet_examples(self):
        self.assertEqual(round(0.0695 * 100 * 0.5 * 0.5, 2), 1.74)  # Polymarket US max per 100
        self.assertAlmostEqual(1 / 5, 0.2)                          # 1¢ minimum over 5 contracts
        self.assertLess(1 / 6, 0.2)                                 # ...so a 0.2¢ gap clears at 6
        self.assertEqual(math.ceil(0.3), 1)                         # Kalshi pays 1¢ on a 0.3¢ fee
        self.assertEqual(round(0.3), 0)                             # Polymarket US half-even pays 0¢

    def test_fee_sheet_size_floor_needs_minimum_fee(self):
        # "a 0.2¢ gap needs about six contracts" holds only while the fee is its 1¢ minimum,
        # i.e. 0.07·6·P(1−P) ≤ 1¢. At P = 0.50 six contracts cost 11¢ (1.83¢ each).
        self.assertEqual(math.ceil(0.07 * 6 * 0.25 * 100), 11)
        self.assertLess(0.07 * 6 * 0.024 * 0.976 * 100, 1)
        self.assertGreater(0.07 * 6 * 0.025 * 0.975 * 100, 1)


if __name__ == "__main__":
    unittest.main()
