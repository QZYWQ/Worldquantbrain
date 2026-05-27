#!/usr/bin/env python3
"""
Gross Profitability Premium — 24h Batch Mining v2

Economic logic: Gross Profit / Total Assets predicts cross-section of returns.
High gross profitability → competitive advantage, lower risk, market underreaction.

Fields:
  gross_income_reported_value (analyst4, 69.5% cov, 184 alphas)
  total_assets_amount (analyst4, 80.4% cov, 158 alphas)
  gross_income_max (analyst4, 68% cov, 17 alphas — virgin)
  gross_income_avg (analyst4, 68% cov, 5 alphas — virgin)

Usage: python3 scripts/gp_24h_batch_v2.py
"""
import json, time
from datetime import datetime
from pathlib import Path

PROJECT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
TS = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT = PROJECT / "runs" / "overnight-mining" / "2026-05-26-gp-24h-v2"
OUT.mkdir(parents=True, exist_ok=True)

BASE = {
    "instrumentType":"EQUITY","region":"USA","universe":"TOP3000",
    "delay":1,"truncation":0.08,"pasteurization":"ON",
    "testPeriod":"P0Y","unitHandling":"VERIFY","nanHandling":"ON",
    "language":"FASTEXPR","visualization":False,
}

from machine_lib import login
s = login()

def sim(expr, name, decay=0, neut="NONE"):
    """Submit + poll up to 10 min. Returns result dict or None."""
    payload = {"type":"REGULAR","settings":dict(BASE, decay=decay, neutralization=neut),"regular":expr}
    resp = s.post("https://api.worldquantbrain.com/simulations", json=payload)
    if resp.status_code != 201:
        print("    ❌ HTTP %d" % resp.status_code, flush=True)
        return None
    url = resp.headers.get("Location")
    for i in range(120):
        prog = s.get(url)
        if prog.headers.get("Retry-After"):
            time.sleep(float(prog.headers["Retry-After"])); continue
        data = prog.json()
        st = data.get("status")
        aid = data.get("alpha")
        if st in ("COMPLETE","WARNING") and aid:
            ad = s.get(f"https://api.worldquantbrain.com/alphas/{aid}").json()
            im = ad.get("is",{})
            r = {"alpha_id":aid, "name":name, "expression":expr,
                 "sharpe":im.get("sharpe"), "fitness":im.get("fitness"),
                 "turnover":im.get("turnover"), "margin":im.get("margin"),
                 "decay":decay, "neut":neut,
                 "longCount":im.get("longCount"),"shortCount":im.get("shortCount")}
            print("    ✓ S=%.3f F=%.3f TVR=%.4f (%s)" % (r["sharpe"],r["fitness"],r["turnover"],aid), flush=True)
            return r
        elif st == "ERROR":
            err = data.get("error","?")
            print("    ❌ ERROR: %s" % err, flush=True)
            return None
        time.sleep(5)
    print("    ⏰ TIMEOUT", flush=True)
    return None

# =============================================================
# Variants — grouped by phase
# =============================================================
# Helper expression builders
def e(numer, denom=None, wrapper="", group=""):
    """Build an expression: wrapper(numer/denom) + rank/group_rank"""
    if denom:
        exp = "(%s) / add(abs(%s), 1)" % (numer, denom)
    else:
        exp = numer
    if wrapper: exp = "%s(%s)" % (wrapper, exp)
    if group:
        return "group_rank(%s, %s)" % (exp, group)
    return "rank(%s)" % exp

# analyst4 gross income fields
GI = "gross_income_reported_value"
GI_MAX = "gross_income_max"
GI_AVG = "gross_income_avg"
GRIC = "anl4_gric_mean"
TA = "total_assets_amount"

# fundamental6 fallback — constructed gross profit: revenue - cogs
REV = "revenue"
COGS = "cogs"
ASST = "assets"

P1 = [  # Phase 1: Baseline
    ("p1_gir_mkt",     e(GI, TA, "", "market"),                             0, "MARKET"),
    ("p1_gir_raw",     e(GI, TA, "", ""),                                    0, "NONE"),
    ("p1_gir_ind",     e(GI, TA, "", "industry"),                            0, "INDUSTRY"),
    ("p1_gir_sind",    e(GI, TA, "", "subindustry"),                         0, "SUBINDUSTRY"),
    ("p1_gir_flip",    "-" + e(GI, TA, "", "subindustry"),                   0, "SUBINDUSTRY"),
    ("p1_gimax_sind",  e(GI_MAX, TA, "", "subindustry"),                     0, "SUBINDUSTRY"),
    ("p1_giavg_sind",  e(GI_AVG, TA, "", "subindustry"),                     0, "SUBINDUSTRY"),
    ("p1_gric_sind",   e(GRIC, TA, "", "subindustry"),                        0, "SUBINDUSTRY"),
    ("p1_const_ind",   e("(%s - %s)" % (REV, COGS), TA, "", "industry"),     0, "INDUSTRY"),
    ("p1_const_sind",  e("(%s - %s)" % (REV, COGS), TA, "", "subindustry"),  0, "SUBINDUSTRY"),
]

P2 = [  # Phase 2: ts_rank / smoothing
    ("p2_gir_tr126",   e(GI, TA, "ts_rank(%s, 126)", "subindustry"),         6, "SUBINDUSTRY"),
    ("p2_gir_tr252",   e(GI, TA, "ts_rank(%s, 252)", "subindustry"),         6, "SUBINDUSTRY"),
    ("p2_gir_tr504",   e(GI, TA, "ts_rank(%s, 504)", "subindustry"),         6, "SUBINDUSTRY"),
    ("p2_gir_tzs252",  e(GI, TA, "ts_zscore(%s, 252)", "subindustry"),      6, "SUBINDUSTRY"),
    ("p2_gimax_tr252", e(GI_MAX, TA, "ts_rank(%s, 252)", "subindustry"),     6, "SUBINDUSTRY"),
    ("p2_giavg_tr252", e(GI_AVG, TA, "ts_rank(%s, 252)", "subindustry"),     6, "SUBINDUSTRY"),
    ("p2_const_tr252", e("(%s - %s)" % (REV, COGS), TA, "ts_rank(%s, 252)", "subindustry"), 6, "SUBINDUSTRY"),
]

P3 = [  # Phase 3: Alternative definitions
    ("p3_gir_assets",  e(GI, "assets", "", "subindustry"),                      6, "SUBINDUSTRY"),
    ("p3_gir_margin",  e(GI, "revenue", "", "subindustry"),                     6, "SUBINDUSTRY"),
    ("p3_gir_d126",    "group_rank(ts_delta(%s, 126), subindustry)" % e(GI, TA, "", ""), 6, "SUBINDUSTRY"),
    ("p3_gir_d252",    "group_rank(ts_delta(%s, 252), subindustry)" % e(GI, TA, "", ""), 6, "SUBINDUSTRY"),
    ("p3_gir_zsc",     "ts_zscore(group_rank(%s, subindustry), 252)" % e(GI, TA, "", ""), 6, "SUBINDUSTRY"),
    ("p3_const_d126",  "group_rank(ts_delta(%s, 126), subindustry)" % e("(%s - %s)" % (REV, COGS), TA, "", ""), 6, "SUBINDUSTRY"),
]

P4 = [  # Phase 4: Upgrade wrappers
    ("p4_densify_d0",  e(GI, TA, "", "densify(bucket(rank(cap), range='0.1,1,0.1'))"),   0, "INDUSTRY"),
    ("p4_densify_d3",  e(GI, TA, "", "densify(bucket(rank(cap), range='0.1,1,0.1'))"),   3, "INDUSTRY"),
    ("p4_densify_d6",  e(GI, TA, "", "densify(bucket(rank(cap), range='0.1,1,0.1'))"),   6, "INDUSTRY"),
    ("p4_decay1",      e(GI, TA, "", "subindustry"),                                     1, "SUBINDUSTRY"),
    ("p4_decay3",      e(GI, TA, "", "subindustry"),                                     3, "SUBINDUSTRY"),
    ("p4_decay15",     e(GI, TA, "", "subindustry"),                                     15, "SUBINDUSTRY"),
    ("p4_decay30",     e(GI, TA, "", "subindustry"),                                     30, "SUBINDUSTRY"),
    ("p4_rank_wrap",   "rank(group_rank(%s, subindustry))" % e(GI, TA, "", ""),           0, "SUBINDUSTRY"),
    ("p4_zscore_wrap", "zscore(group_rank(%s, subindustry))" % e(GI, TA, "", ""),         0, "SUBINDUSTRY"),
    ("p4_giavg_dens0", e(GI_AVG, TA, "", "densify(bucket(rank(cap), range='0.1,1,0.1'))"), 0, "INDUSTRY"),
    ("p4_gimax_dens0", e(GI_MAX, TA, "", "densify(bucket(rank(cap), range='0.1,1,0.1'))"), 0, "INDUSTRY"),
]

ALL = P1 + P2 + P3 + P4

ALL = P1 + P2 + P3 + P4
print("GP 24h v2 — %d variants" % len(ALL), flush=True)

results = []
for pn, variants, label in [(1, P1, "Baseline"), (2, P2, "ts_rank"), (3, P3, "Alternative"), (4, P4, "Upgrade")]:
    print("\n===== Phase %d: %s (%d vars) =====" % (pn, label, len(variants)), flush=True)
    for name, expr, decay, neut in variants:
        print("  ▶ %-20s" % name, end=" ", flush=True)
        res = sim(expr, name, decay, neut)
        if res: results.append(res)
        time.sleep(3)  # be kind to the API

# Save + summarize
report = {
    "generated_at": datetime.now().isoformat(),
    "total": len(ALL), "passed": len(results),
    "results": sorted(results, key=lambda x: -(x.get("sharpe") or 0)),
}
report_path = OUT / ("gp_24h_v2_%s.json" % TS)
with open(str(report_path), "w") as f:
    json.dump(report, f, indent=2, default=str)

print("\n" + "="*70, flush=True)
print("DONE: %d/%d passed" % (len(results), len(ALL)), flush=True)
print("S>=1.0: %d" % len([r for r in results if (r.get("sharpe") or 0) >= 1.0]), flush=True)
print("="*70, flush=True)
for i, r in enumerate(sorted(results, key=lambda x: -(x.get("sharpe") or 0))[:15]):
    print("#%2d %-20s S=%.3f F=%.3f TVR=%.4f [%s %s]" % (
        i+1, r["name"], r["sharpe"] or 0, r["fitness"] or 0, r["turnover"] or 0,
        r["alpha_id"], "d%d" % r["decay"]), flush=True)
print("="*70, flush=True)
