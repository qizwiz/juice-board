"""Invariants the published figures should satisfy. Run: python3 -m unittest discover -s _audit -v

The tests under BoardAgainstItsOwnLabels FAIL on the current board.html. They are the spec for the
generator that writes board.html; that generator is not in this repository, so there is no code
here to fix them in.
"""
import math
import statistics
import unittest

import board_audit as b

SNAPS = b.snapshots()
PAGE = SNAPS[-1][2]


class SiteArithmetic(unittest.TestCase):
    """Figures on the Markdown pages that can be recomputed from other figures on the same pages."""

    def test_experiment_rates(self):
        self.assertEqual(round(100 * 976 / 3863, 1), 25.3)
        self.assertEqual(round(100 * 1219 / 3863, 1), 31.6)
        self.assertEqual(round(100 * 2 / 12481, 3), 0.016)
        self.assertEqual(976 - 9, 967)
        self.assertEqual(12481 - 2, 12479)
        self.assertLessEqual(3863 + 7, 244 * 16)
        self.assertLessEqual(12481 + 65, 716 * 19)
        self.assertEqual(16 + 19, 35)  # engineering.md: "35 certified so far"

    def test_best_carry(self):
        edge, q, days = 2.27, 500, 773
        profit, locked = edge * q / 100, (100 - edge) * q / 100
        self.assertAlmostEqual(profit, 11.35)
        self.assertAlmostEqual(locked, 488.65)
        self.assertEqual(round(100 * profit / locked * 365 / days, 1), 1.1)

    def test_in_play_crosses(self):
        self.assertAlmostEqual((5 - 4.94) / 5 * 100, 1.2)
        self.assertAlmostEqual((5 - 4.99) / 5 * 100, 0.2)

    def test_rule_of_three(self):
        for n, shown in ((807, 0.4), (540, 0.6), (330, 0.9), (138, 2.2), (77, 3.9)):
            self.assertEqual(round(300 / n, 1), shown, n)
        self.assertEqual(round(100 / 453, 1), 0.2)

    def test_fee_sheet(self):
        self.assertEqual(round(0.0695 * 100 * 0.25, 2), 1.74)
        self.assertEqual(math.ceil(0.3), 1)              # Kalshi, ceiling
        self.assertEqual(round(0.003, 2), 0.0)           # Polymarket US, half-even to the cent
        self.assertEqual(b.kalshi_fee_cents(0.5, 100), 1.75)

    def test_point_two_cent_gap_breaks_even_at_five(self):
        """fees.md: 'a 0.2c gap needs about six contracts to break even'. With the 1c minimum fee it
        nets exactly zero at five and is first positive at six."""
        net = lambda q: 0.2 * q - 1.0
        self.assertAlmostEqual(net(5), 0.0)
        self.assertGreater(net(6), 0)


class BoardRowArithmetic(unittest.TestCase):
    """Per-row numbers on every committed snapshot. These pass."""

    def test_every_row_recomputes(self):
        bad = [(sha[:7], r["pair"], c, d) for _, sha, p in SNAPS for r in p["rows"]
               for c, d in b.row_findings(r) if c != "cap_label"]
        self.assertEqual(bad, [])

    def test_page_totals(self):
        bad = [(sha[:7], c, d) for _, sha, p in SNAPS for c, d in b.page_findings(p)]
        self.assertEqual(bad, [])

    def test_fill_record_bounds(self):
        for _, _, p in SNAPS:
            f = p["fill"]
            self.assertLessEqual(f["filled"], f["attempted"])
            self.assertLessEqual(f["attempted"], b.SIZE_CAP * f["decisions"])


class BoardAgainstItsOwnLabels(unittest.TestCase):
    """Each of these fails today; see _audit/REPORT.md."""

    def test_size_label_is_not_the_cap(self):
        """'500 contracts (the most that stays under $1 walking both books)' while the best level
        alone holds more than 500."""
        bad = [(r["pair"], int(r["depth"])) for r in PAGE["rows"]
               if r["q_exec"] == b.SIZE_CAP and r["depth"] > b.SIZE_CAP]
        self.assertEqual(bad, [])

    def test_size_floor_text(self):
        """'size floor around q>=N': the smallest q at which the unrounded Kalshi fee reaches 1c."""
        bad = []
        for r in PAGE["rows"]:
            ok = set()
            for d in range(-50, 51):  # shown price is rounded to 3 dp
                p = r["pk"] + d / 1e5
                ok.add(max(r["qmin"], math.ceil(1 / (100 * b.KALSHI_RATE * r["M"] * p * (1 - p)))))
            if r["floor_text"] not in ok:
                bad.append((r["pair"], r["floor_text"], sorted(ok)))
        self.assertEqual(bad, [])

    def test_counts_accrue(self):
        """'Counts accrue over every row recorded since 2026-09-27'."""
        for key in ("replayed", "decisions", "attempted", "net_usd"):
            series = [p["fill"][key] for _, _, p in SNAPS]
            with self.subTest(key=key):
                self.assertEqual(series, sorted(series))

    def test_record_covers_its_since_date(self):
        self.assertEqual(b.window_findings(PAGE, PAGE["generated"]), [])

    def test_scan_counter_advances(self):
        (t0, _, first), (t1, _, last) = SNAPS[0], SNAPS[-1]
        if t1 - t0 > 3600:
            self.assertGreater(last["strip"]["scans"], first["strip"]["scans"])

    def test_fixed_rows_keep_their_sub_dollar_count(self):
        totals = {(p["strip"]["rows"], sum(r["sub_num"] for r in p["rows"])) for _, _, p in SNAPS}
        self.assertEqual(len({n for d, n in totals if d == PAGE["strip"]["rows"]}), 1)

    def test_republished_every_ten_minutes(self):
        gaps = [(b_[0] - a[0]) / 60 for a, b_ in zip(SNAPS, SNAPS[1:])]
        self.assertLessEqual(statistics.median(gaps), 11)


if __name__ == "__main__":
    unittest.main()
