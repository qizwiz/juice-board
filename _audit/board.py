"""Parse the published board.html into plain numbers so the audit can recompute them.

Lives under _audit/ so Jekyll never publishes it. Standard library only.
"""
import html
import os
import re
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROW_RE = re.compile(r'<tr class="row"([^>]*)>(.*?)</tr>\s*<tr class="detail" hidden>(.*?)</tr>', re.S)


def _text(fragment):
    t = re.sub(r"<svg.*?</svg>", "", fragment, flags=re.S)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)))


def parse(src):
    """Return {'rows': [...], 'strip': {...}, 'paper': {...}, 'generated': int, 'footer': str, ...}."""
    rows = []
    for m in ROW_RE.finditer(src):
        a = dict(re.findall(r'data-(\w+)="([^"]*)"', m.group(1)))
        body = _text(m.group(2))
        detail = _text(m.group(3))
        num = lambda k: float(a[k]) if a.get(k, "") != "" else None
        legs = re.search(r"Buy (YES|NO) on Kalshi at ([\d.]+) and (YES|NO) on Polymarket at ([\d.]+)", body)
        q = re.search(r"Priced at the executable size, (\d+) contracts", body)
        rate = re.search(r"Polymarket taker rate ([\d.]+)", detail)
        sub, seen = map(int, re.findall(r"(\d+)/(\d+)", body)[-1])
        rows.append({
            "pair": a["pair"], "verdict": a["verdict"], "exp": a["exp"],
            "net": num("net"), "gross": num("gross"), "kvig": num("kvig"), "pvig": num("pvig"),
            "depth": int(a["depth"]), "edge": num("edge"), "days": num("days"), "ann": num("ann"),
            "pstar": num("pstar"), "persist": num("persist"),
            "k_price": float(legs.group(2)), "p_price": float(legs.group(4)),
            "q": int(q.group(1)) if q else None, "rate": float(rate.group(1)),
            "sub": sub, "seen": seen, "text": body,
        })
    strip = {k: int(v) for k, v in re.findall(r'<div class="k">([^<]+)</div><div class="v">(\d+)<small>', src)}
    scans, nrows = map(int, re.search(r'Scans</div><div class="v">(\d+)<small> · (\d+) rows', src).groups())
    paper = re.search(
        r"([\d,]+)<small> rows replayed · (\d+) pairs · ([\d\- :]+)</small>.*?"
        r"<div class=\"v\">(\d+)%<small> filled.*?<div class=\"res\">(\d+) decisions on (\d+) of (\d+) pairs · "
        r"([\d,]+) of ([\d,]+) contracts · legged ([\d,]+) · net \$([\d,.]+) · ≈ \$([\d,]+) locked to settlement "
        r"\(([\d.]+)% in total", src, re.S)
    to_i = lambda s: int(s.replace(",", ""))
    return {
        "rows": rows,
        "strip": strip,
        "scans": scans,
        "nrows": nrows,
        "paper": {
            "replayed": to_i(paper.group(1)), "pairs": int(paper.group(2)), "as_of": paper.group(3),
            "filled_pct": int(paper.group(4)), "decisions": int(paper.group(5)),
            "pairs_with_decisions": int(paper.group(6)), "pairs_total": int(paper.group(7)),
            "contracts_filled": to_i(paper.group(8)), "contracts_wanted": to_i(paper.group(9)),
            "legged": to_i(paper.group(10)), "net": float(paper.group(11).replace(",", "")),
            "locked": to_i(paper.group(12)), "total_pct": float(paper.group(13)),
        },
        "generated": int(re.search(r'data-generated="(\d+)"', src).group(1)),
        "footer_generated": re.search(r"generated (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", src).group(1),
        "cadence_s": int(re.search(r"read every ~(\d+) s", src).group(1)),
        "depth_legend_max": int(re.search(r"log scale, max (\d+)", src).group(1)),
        "edge_tooltip": re.search(r'data-k="edge" title="([^"]+)"', src).group(1),
    }


def load(path=None):
    with open(path or os.path.join(REPO, "board.html"), encoding="utf-8") as f:
        return parse(f.read())


def history():
    """Every committed snapshot of board.html, oldest first: [(commit_time, parsed), ...]."""
    out = subprocess.check_output(
        ["git", "-C", REPO, "log", "--reverse", "--format=%H %ct", "--", "board.html"], text=True)
    snaps = []
    for line in out.split("\n"):
        if not line:
            continue
        sha, ct = line.split()
        src = subprocess.check_output(["git", "-C", REPO, "show", sha + ":board.html"], text=True)
        snaps.append((int(ct), parse(src)))
    return snaps
