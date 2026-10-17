"""Recompute the figures on board.html and check them against each other.

Stdlib only. Jekyll skips underscore directories, so nothing here is published.

    python3 _audit/board_audit.py            # audit the working-tree board.html
    python3 _audit/board_audit.py --history  # also walk every committed snapshot
"""
import html
import math
import re
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KALSHI_RATE = 0.07
DIVERGE_LOSS_C = 50.0  # footer: "assumes a -50c/contract loss"
DUST_USD = 1.0
SIZE_CAP = 500


def _num(s):
    return float(s.replace(",", "").replace("$", ""))


def text_of(fragment):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment))).strip()


def parse(src):
    """Return {'rows': [...], 'strip': {...}, 'fill': {...}, 'generated': int, 'depth_max': int}."""
    rows = []
    for m in re.finditer(r'<tr class="row"([^>]*)>(.*?)</tr>\s*<tr class="detail"[^>]*>(.*?)</tr>', src, re.S):
        attrs = dict(re.findall(r'data-([a-z]+)="([^"]*)"', m.group(1)))
        detail = text_of(m.group(3))
        r = {k: attrs[k] for k in ("verdict", "pair", "exp")}
        for k in ("rank", "net", "gross", "kvig", "pvig", "depth", "edge", "ann", "pstar", "persist"):
            r[k] = float(attrs[k]) if attrs.get(k, "") != "" else None
        r["days"] = float(attrs["days"]) if attrs.get("days") else None
        rm = re.search(r"Buy (YES|NO) on Kalshi at ([\d.]+) and (YES|NO) on Polymarket at ([\d.]+): "
                       r"gross ([\d.]+)", detail)
        r["pk"], r["pp"], r["gross_cost"] = float(rm.group(2)), float(rm.group(4)), float(rm.group(5))
        r["rate"] = float(re.search(r"Polymarket taker rate ([\d.]+)", detail).group(1))
        r["M"] = float(re.search(r"× M ([\d.]+)", detail).group(1))
        r["qmin"] = int(re.search(r"q_min (\d+)", detail).group(1))
        qm = re.search(r"Priced at the executable size, (\d+) contracts", detail)
        r["q_exec"] = int(qm.group(1)) if qm else None
        fm = re.search(r"size floor around q≥(\d+)", detail)
        r["floor_text"] = int(fm.group(1)) if fm else None
        sm = re.search(r"(\d+) rows seen for this pair", detail)
        r["rows_seen"] = int(sm.group(1))
        cells = [text_of(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", m.group(2), re.S)]
        sub = next(c for c in cells if re.fullmatch(r"\d+/\d+", c))
        r["sub_num"], r["sub_den"] = map(int, sub.split("/"))
        rows.append(r)

    body = text_of(src[src.find("<body"):])
    strip = {}
    for key in ("Live edge", "Carry-negative", "Dust", "Thin", "No edge"):
        strip[key] = int(re.search(re.escape(key) + r" (\d+)", body).group(1))
    sm = re.search(r"Scans (\d+) · (\d+) rows", body)
    strip["scans"], strip["rows"] = int(sm.group(1)), int(sm.group(2))

    fill = {}
    fm = re.search(r"Paper fill record · simulated ([\d,]+) rows replayed · (\d+) pairs · ([\d-]+ [\d:]+)", body)
    fill["replayed"], fill["pairs"], fill["stamp"] = int(_num(fm.group(1))), int(fm.group(2)), fm.group(3)
    lm = re.search(r"Long-dated \(2028 and later\) (\d+)% filled .*?median gap between books is ~(\d+) s\)"
                   r".*?(\d+) decisions on (\d+) of (\d+) pairs · ([\d,]+) of ([\d,]+) contracts · legged ([\d,]+)"
                   r" · net \$([\d,.]+) · ≈ \$([\d,]+) locked to settlement \(([\d.]+)% in total", body)
    (fill["pct_filled"], fill["median_gap_s"], fill["decisions"], fill["dec_pairs"], fill["of_pairs"],
     fill["filled"], fill["attempted"], fill["legged"], fill["net_usd"], fill["locked_usd"],
     fill["pct_total"]) = [_num(g) for g in lm.groups()]
    fill["short_no_rows"] = "Short-dated (settle ≤ 14 d) — no rows" in body
    fill["since"] = re.search(r"every row recorded since ([\d-]+)", body).group(1)
    header_gap = int(re.search(r"passive books read every ~(\d+) s", body).group(1))
    return {
        "rows": rows, "strip": strip, "fill": fill, "header_gap_s": header_gap,
        "generated": int(re.search(r'<body data-generated="(\d+)"', src).group(1)),
        "depth_max": int(re.search(r"log scale, max (\d+)", body).group(1)),
    }


# --- the fee and edge arithmetic, per fees.md and the board footer ---------------------------

def kalshi_fee_cents(price, q, M=1.0):
    """round-up(M x 0.07 x C x P(1-P)) to the cent, per order; returns cents per contract."""
    raw_cents = 100 * M * KALSHI_RATE * q * price * (1 - price)
    return math.ceil(raw_cents - 1e-9) / q


def poly_fee_cents(price, rate):
    return 100 * rate * price * (1 - price)


def priced_size(r):
    return r["q_exec"] if r["q_exec"] else r["qmin"]


def row_findings(r):
    """Return a list of (check, detail) failures for one board row."""
    out = []
    q = priced_size(r)
    # gross: shown prices are rounded to 3 dp, so allow 0.05c per leg
    if abs(100 * (1 - r["pk"] - r["pp"]) - r["gross"]) > 0.1 + 1e-9:
        out.append(("gross", f"100*(1-{r['pk']}-{r['pp']}) != {r['gross']}"))
    if abs(100 * (1 - r["gross_cost"]) - r["gross"]) > 0.005 + 1e-9:  # gross cost shown to 4 dp
        out.append(("gross_cost", f"{r['gross_cost']} vs gap {r['gross']}"))
    # Kalshi fee: admissible interval over the 3-dp rounding of the shown price
    lo, hi = sorted(kalshi_fee_cents(r["pk"] + d, q, r["M"]) for d in (-0.0005, 0.0005))
    cands = {kalshi_fee_cents(r["pk"] + d / 1e4, q, r["M"]) for d in range(-5, 6)}
    if not any(abs(c - r["kvig"]) < 1e-6 for c in cands) and not (lo - 1e-6 <= r["kvig"] <= hi + 1e-6):
        out.append(("kvig", f"kvig {r['kvig']} not reachable at q={q}, P≈{r['pk']} (range {lo:.4f}–{hi:.4f})"))
    plo, phi = sorted(poly_fee_cents(r["pp"] + d, r["rate"]) for d in (-0.0005, 0.0005))
    if not (min(plo, phi) - 1e-4 <= r["pvig"] <= max(plo, phi) + 1e-4):
        out.append(("pvig", f"pvig {r['pvig']} vs {poly_fee_cents(r['pp'], r['rate']):.4f}"))
    if abs(r["gross"] - r["kvig"] - r["pvig"] - r["net"]) > 1.5e-4:
        out.append(("net", f"{r['gross']}-{r['kvig']}-{r['pvig']} != {r['net']}"))
    if abs(r["net"] * q / 100 - r["edge"]) > 0.00005 * q / 100 + 1.5e-4:  # net shown to 4 dp
        out.append(("edge", f"{r['net']}*{q}/100 != {r['edge']}"))
    if r["net"] > 0 and abs(r["net"] / DIVERGE_LOSS_C - r["pstar"]) > 1e-5:
        out.append(("pstar", f"net/50={r['net'] / 50:.5f} vs {r['pstar']}"))
    if abs(100 * r["sub_num"] / r["sub_den"] - r["persist"]) > 0.006:
        out.append(("persist", f"{r['sub_num']}/{r['sub_den']} vs {r['persist']}%"))
    if r["sub_den"] != r["rows_seen"]:
        out.append(("rows_seen", f"{r['sub_den']} vs {r['rows_seen']}"))
    # verdict, in the footer's test order
    expect = ("NO EDGE" if r["net"] <= 0 else "DUST" if r["edge"] < DUST_USD
              else "CARRY-NEGATIVE" if r["ann"] < 4 else "LIVE EDGE")
    if r["verdict"] != expect and r["verdict"] != "THIN":
        out.append(("verdict", f"{r['verdict']} but rules give {expect}"))
    # label: "N contracts (the most that stays under $1 walking both books)"
    if r["q_exec"] == SIZE_CAP and r["depth"] > SIZE_CAP:
        out.append(("cap_label", f"says {SIZE_CAP} is the most under $1, best level alone holds {int(r['depth'])}"))
    return out


def page_findings(p):
    out = []
    rows, s, f = p["rows"], p["strip"], p["fill"]
    counts = {"Live edge": "LIVE EDGE", "Carry-negative": "CARRY-NEGATIVE", "Dust": "DUST",
              "Thin": "THIN", "No edge": "NO EDGE"}
    for k, v in counts.items():
        n = sum(r["verdict"] == v for r in rows)
        if s[k] != n:
            out.append(("strip_count", f"{k} {s[k]} vs {n} rows"))
    if s["rows"] != sum(r["rows_seen"] for r in rows):
        out.append(("strip_rows", f"{s['rows']} vs sum {sum(r['rows_seen'] for r in rows)}"))
    if max(r["rows_seen"] for r in rows) > s["scans"]:
        out.append(("strip_scans", "a pair has more rows than scans"))
    if p["depth_max"] != max(int(r["depth"]) for r in rows):
        out.append(("depth_max", f"{p['depth_max']} vs {max(int(r['depth']) for r in rows)}"))
    pct = 100 * f["filled"] / f["attempted"]
    if round(pct) != f["pct_filled"]:
        out.append(("pct_filled", f"{f['filled']:.0f}/{f['attempted']:.0f}={pct:.2f}% vs {f['pct_filled']:.0f}%"))
    tot = 100 * f["net_usd"] / f["locked_usd"]
    if round(tot, 2) != f["pct_total"]:
        out.append(("pct_total", f"{tot:.3f}% vs {f['pct_total']}%"))
    if f["of_pairs"] != len(rows) or f["pairs"] != len(rows):
        out.append(("fill_pairs", f"{f['pairs']}/{f['of_pairs']} vs {len(rows)}"))
    if f["dec_pairs"] > sum(r["sub_num"] > 0 for r in rows):
        out.append(("dec_pairs", "decisions on more pairs than ever priced under $1"))
    return out


# --- history ----------------------------------------------------------------------------------

def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout


def snapshots():
    """[(commit_unix_time, sha, parsed_page)] oldest first, for every commit that touched board.html."""
    out = []
    lines = git("log", "--reverse", "--format=%ct %H", "--", "board.html").strip().splitlines()
    for line in lines:
        ct, sha = line.split()
        out.append((int(ct), sha, parse(git("show", f"{sha}:board.html"))))
    return out


def history_findings(snaps):
    out = []
    gaps = [b[0] - a[0] for a, b in zip(snaps, snaps[1:])]
    if gaps and statistics.median(gaps) > 11 * 60:
        out.append(("cadence", f"'republished every 10 minutes': median commit gap {statistics.median(gaps) / 60:.1f} min "
                               f"(min {min(gaps) / 60:.1f}, max {max(gaps) / 60:.1f}, n={len(gaps)})"))
    accrue = ("replayed", "decisions", "filled", "attempted", "net_usd", "locked_usd")
    for key in accrue:
        drops = [(a[2]["fill"][key], b[2]["fill"][key], b[1][:7]) for a, b in zip(snaps, snaps[1:])
                 if b[2]["fill"][key] < a[2]["fill"][key]]
        if drops:
            out.append(("accrue_" + key, f"'counts accrue' but {key} fell {len(drops)} times, e.g. "
                                         f"{drops[0][0]:,.2f} -> {drops[0][1]:,.2f} at {drops[0][2]}"))
    first, last = snaps[0][2], snaps[-1][2]
    if len(snaps) > 1 and first["strip"]["scans"] == last["strip"]["scans"]:
        hours = (snaps[-1][0] - snaps[0][0]) / 3600
        out.append(("scans_frozen", f"Scans {last['strip']['scans']} unchanged across {len(snaps)} snapshots "
                                    f"over {hours:.1f} h (at ~{last['header_gap_s']} s/scan, "
                                    f"~{hours * 3600 / last['header_gap_s']:.0f} scans expected)"))
    # Pair labels are rank positions, not identities, so compare page totals: a fixed set of rows
    # cannot change how many of its rows priced under $1.
    totals = [(s[2]["strip"]["rows"], sum(r["sub_num"] for r in s[2]["rows"])) for s in snaps]
    dens = {d for d, _ in totals}
    nums = [n for _, n in totals]
    if len(dens) == 1 and len(set(nums)) > 1:
        out.append(("fixed_denominator", f"sub-$1 rows summed over pairs moved {nums[0]} -> {nums[-1]} "
                                         f"(range {min(nums)}..{max(nums)}) while total rows stayed {dens.pop()}"))
    return out


def window_findings(p, today_unix):
    """The site's own cadence against its own 'since 2026-09-27'."""
    import datetime as dt
    since = dt.datetime.fromisoformat(p["fill"]["since"]).replace(tzinfo=dt.timezone.utc).timestamp()
    days = (today_unix - since) / 86400
    span_days = p["strip"]["scans"] * p["header_gap_s"] / 86400
    if span_days < 0.5 * days:
        return [("window", f"{p['strip']['scans']} scans x ~{p['header_gap_s']} s = {span_days:.1f} days of data, "
                           f"but the record claims every row since {p['fill']['since']} ({days:.1f} days)")]
    return []


def main(argv):
    page = parse((ROOT / "board.html").read_text())
    problems = []
    for r in page["rows"]:
        problems += [(r["pair"], c, d) for c, d in row_findings(r)]
    problems += [("page", c, d) for c, d in page_findings(page)]
    problems += [("page", c, d) for c, d in window_findings(page, page["generated"])]
    if "--history" in argv:
        snaps = snapshots()
        for ct, sha, p in snaps:
            for r in p["rows"]:
                problems += [(f"{sha[:7]}:{r['pair']}", c, d) for c, d in row_findings(r) if c != "cap_label"]
            problems += [(f"{sha[:7]}", c, d) for c, d in page_findings(p)]
        problems += [("history", c, d) for c, d in history_findings(snaps)]
        print(f"{len(snaps)} snapshots; fill-record series (decisions, replayed, median gap s):")
        print("  " + ", ".join(f"{p['fill']['decisions']:.0f}/{p['fill']['replayed']}/{p['fill']['median_gap_s']:.0f}"
                               for _, _, p in snaps))
    for who, check, detail in problems:
        print(f"FAIL {who:16} {check:18} {detail}")
    print(f"{len(problems)} finding(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
