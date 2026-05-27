#!/usr/bin/env python3
"""
Gross Profitability Premium — 24h Batch Mining (Phased Execution)

Economic logic: Gross Profit / Total Assets predicts cross-section of returns.
High gross profitability → competitive advantage, lower risk, market underreaction.

Core fields:
  - gross_income_reported_value (analyst4, 69.5% cov, 184 alphas)
  - total_assets_amount (analyst4, 80.4% cov, 158 alphas)
  Both from analyst4 → consistent dataset, very low crowding.

Phases:
  1: Baseline confirmation — level signal, sign, group
  2: Smoothing & ts_rank position
  3: Alternative numerator/denominator
  4: Upgrade wrappers (densify, rank, decay)
  5: SC verification & ranking

Usage:
  python3 scripts/gp_24h_batch.py
"""
import json, time
from datetime import datetime
from pathlib import Path
from machine_lib import login, set_alpha_properties

PROJECT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_DIR = PROJECT / "runs" / "overnight-mining" / f"2026-05-26-gp-24h"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = PROJECT / "runs" / "simulation-captures"

# ---- Helpers ----
BASE_SETTINGS = {
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,
    "truncation": 0.08,
    "pasteurization": "ON",
    "testPeriod": "P0Y",
    "unitHandling": "VERIFY",
    "nanHandling": "ON",
    "language": "FASTEXPR",
    "visualization": False,
}

def ws(field, window=252, std=4):
    return "winsorize(ts_backfill(%s, %d), std=%d)" % (field, window, std)

def sa(x):
    """Safe denominator: add(abs(x), 1) to avoid division by zero."""
    return "add(abs(%s), 1)" % x

# analyst4 fields (primary — low crowding, high coverage)
GI_REPORTED = ws("gross_income_reported_value", 252, 3)  # 69.5% cov
GI_MAX = ws("gross_income_max", 252, 3)  # 68% cov, 17 alphas! virgin
GI_AVG = ws("gross_income_avg", 252, 3)  # 68% cov, 5 alphas! virgin
GRIC_MEAN = ws("anl4_gric_mean", 252, 3)  # 60.3% cov

# Total assets from analyst4 (80.35% cov, 158 alphas — matches dataset)
TA = ws("total_assets_amount", 252, 3)

# fundamental6 fallbacks
F6_GP = ws("fnd6_newa1v1300_gp", 252, 3)  # gross profit, 50% cov
F6_REV = ws("revenue", 252, 3)
F6_COGS = ws("cogs", 252, 3)
F6_ASST = ws("assets", 252, 3)

# ---- Core ratio helper ----
def ratio(numerator, denominator):
    return "divide(%s, %s)" % (numerator, sa(denominator))

def gr_ratio(field=GI_REPORTED):
    """Gross profitability ratio: gross_income / total_assets"""
    return ratio(field, TA)

def gr_const(field_rev=F6_REV, field_cogs=F6_COGS):
    """Constructed gross profit: (revenue - cogs) / assets"""
    gp = "sub(%s, %s)" % (field_rev, field_cogs)
    return "divide(%s, %s)" % (gp, sa(F6_ASST))

# ==============================================================
# Phase 1: Baseline Confirmation
# ==============================================================
GR_REPORTED = gr_ratio(GI_REPORTED)
GR_MAX = gr_ratio(GI_MAX)
GR_AVG = gr_ratio(GI_AVG)
GR_GRIC_MEAN = gr_ratio(GRIC_MEAN)
GR_CONST = gr_const(F6_REV, F6_COGS)

PHASE01 = [
    # -- analyst4 primary --
    ("p1_gir_raw_mkt", "rank(%s)" % GR_REPORTED, 0, "NONE"),
    ("p1_gir_raw_i", "group_rank(%s, industry)" % GR_REPORTED, 0, "INDUSTRY"),
    ("p1_gir_raw_si", "group_rank(%s, subindustry)" % GR_REPORTED, 0, "SUBINDUSTRY"),
    ("p1_gir_flip", "-group_rank(%s, subindustry)" % GR_REPORTED, 0, "SUBINDUSTRY"),
    # -- alternative numerator (analyst4) --
    ("p1_gimax_si", "group_rank(%s, subindustry)" % GR_MAX, 0, "SUBINDUSTRY"),
    ("p1_giavg_si", "group_rank(%s, subindustry)" % GR_AVG, 0, "SUBINDUSTRY"),
    ("p1_gric_si", "group_rank(%s, subindustry)" % GR_GRIC_MEAN, 0, "SUBINDUSTRY"),
    # -- constructed gross profit (fundamental6) --
    ("p1_const_i", "group_rank(%s, industry)" % GR_CONST, 0, "INDUSTRY"),
    ("p1_const_si", "group_rank(%s, subindustry)" % GR_CONST, 0, "SUBINDUSTRY"),
    # -- fnd6_gp directly --
    ("p1_f6gp_i", "group_rank(%s, industry)" % gr_ratio(F6_GP), 0, "INDUSTRY"),
    ("p1_f6gp_si", "group_rank(%s, subindustry)" % gr_ratio(F6_GP), 0, "SUBINDUSTRY"),
    # -- Sign and structure tests --
    ("p1_gir_mkt_d6", "group_rank(%s, market)" % GR_REPORTED, 6, "MARKET"),
    ("p1_gir_mkt_none", "group_rank(%s, market)" % GR_REPORTED, 0, "NONE"),
]

# ==============================================================
# Phase 2: Smoothing & ts_rank Position
# ==============================================================
# For quarterly data, longer smoothing reduces noise
PHASE02 = [
    # Smoothing: ts_mean on ratio
    ("p2_gir_mean63_si", "group_rank(ts_mean(%s, 63), subindustry)" % GR_REPORTED, 6, "SUBINDUSTRY"),
    ("p2_gir_mean126_si", "group_rank(ts_mean(%s, 126), subindustry)" % GR_REPORTED, 6, "SUBINDUSTRY"),
    ("p2_gir_mean252_si", "group_rank(ts_mean(%s, 252), subindustry)" % GR_REPORTED, 6, "SUBINDUSTRY"),
    # ts_rank position
    ("p2_gir_tr126_si", "group_rank(ts_rank(%s, 126), subindustry)" % GR_REPORTED, 6, "SUBINDUSTRY"),
    ("p2_gir_tr252_si", "group_rank(ts_rank(%s, 252), subindustry)" % GR_REPORTED, 6, "SUBINDUSTRY"),
    ("p2_gir_tr504_si", "group_rank(ts_rank(%s, 504), subindustry)" % GR_REPORTED, 6, "SUBINDUSTRY"),
    # ts_zscore alternative
    ("p2_gir_tzs126_si", "group_rank(ts_zscore(%s, 126), subindustry)" % GR_REPORTED, 6, "SUBINDUSTRY"),
    ("p2_gir_tzs252_si", "group_rank(ts_zscore(%s, 252), subindustry)" % GR_REPORTED, 6, "SUBINDUSTRY"),
    # gimax smoothing
    ("p2_gimax_tr252_si", "group_rank(ts_rank(%s, 252), subindustry)" % GR_MAX, 6, "SUBINDUSTRY"),
    ("p2_giavg_tr252_si", "group_rank(ts_rank(%s, 252), subindustry)" % GR_AVG, 6, "SUBINDUSTRY"),
    # constructed smoothing
    ("p2_const_tr252_si", "group_rank(ts_rank(%s, 252), subindustry)" % GR_CONST, 6, "SUBINDUSTRY"),
]

# ==============================================================
# Phase 3: Alternative Definitions
# ==============================================================
def alt_ratio(numerator, denominator_field):
    return "divide(%s, %s)" % (numerator, sa(ws(denominator_field, 252, 3)))

PHASE03 = [
    # Different denominators for analyst4 GI
    ("p3_gir_assets", "group_rank(%s, subindustry)" % alt_ratio(GI_REPORTED, "assets"), 6, "SUBINDUSTRY"),
    ("p3_gir_curassets", "group_rank(%s, subindustry)" % alt_ratio(GI_REPORTED, "assets_curr"), 6, "SUBINDUSTRY"),
    # GI / revenue = gross margin
    ("p3_gir_margin", "group_rank(%s, subindustry)" % ratio(GI_REPORTED, ws("revenue", 252, 3)), 6, "SUBINDUSTRY"),
    # GI / market_cap = earnings yield variant
    ("p3_gir_mktcap", "group_rank(%s, subindustry)" % alt_ratio(GI_REPORTED, "cap"), 6, "SUBINDUSTRY"),
    # Change in GP ratio (delta)
    ("p3_gir_delta126", "group_rank(ts_delta(ts_mean(%s, 63), 126), subindustry)" % GR_REPORTED, 6, "SUBINDUSTRY"),
    ("p3_gir_delta252", "group_rank(ts_delta(ts_mean(%s, 126), 252), subindustry)" % GR_REPORTED, 6, "SUBINDUSTRY"),
    # F6 constructed delta
    ("p3_const_delta126", "group_rank(ts_delta(ts_mean(%s, 63), 126), subindustry)" % GR_CONST, 6, "SUBINDUSTRY"),
    ("p3_const_delta252", "group_rank(ts_delta(ts_mean(%s, 126), 252), subindustry)" % GR_CONST, 6, "SUBINDUSTRY"),
    # F6_GP delta
    ("p3_f6gp_delta126", "group_rank(ts_delta(ts_mean(%s, 63), 126), subindustry)" % gr_ratio(F6_GP), 6, "SUBINDUSTRY"),
    # ts_zscore on ratio — captures relative position within subindustry
    ("p3_gir_zsc_si", "ts_zscore(group_rank(%s, subindustry), 252)" % GR_REPORTED, 6, "SUBINDUSTRY"),
]

# ==============================================================
# Phase 4: Upgrade Wrappers
# ==============================================================
# Best baseline anchor from earlier phases
P1_ANCHOR = GR_REPORTED

PHASE04 = [
    # Densify(bucket(rank(cap))) — size neutrality
    ("p4_densify_d0", "group_rank(%s, densify(bucket(rank(cap), range='0.1,1,0.1')))" % P1_ANCHOR, 0, "INDUSTRY"),
    ("p4_densify_d3", "group_rank(%s, densify(bucket(rank(cap), range='0.1,1,0.1')))" % P1_ANCHOR, 3, "INDUSTRY"),
    ("p4_densify_d6", "group_rank(%s, densify(bucket(rank(cap), range='0.1,1,0.1')))" % P1_ANCHOR, 6, "INDUSTRY"),
    # Decay sweep on best expression
    ("p4_decay1", "group_rank(%s, subindustry)" % P1_ANCHOR, 1, "SUBINDUSTRY"),
    ("p4_decay3", "group_rank(%s, subindustry)" % P1_ANCHOR, 3, "SUBINDUSTRY"),
    ("p4_decay15", "group_rank(%s, subindustry)" % P1_ANCHOR, 15, "SUBINDUSTRY"),
    ("p4_decay30", "group_rank(%s, subindustry)" % P1_ANCHOR, 30, "SUBINDUSTRY"),
    # rank() wrapper — can help SC
    ("p4_rank_wrap", "rank(group_rank(%s, subindustry))" % P1_ANCHOR, 0, "SUBINDUSTRY"),
    # zscore wrapper
    ("p4_zscore_wrap", "zscore(group_rank(%s, subindustry))" % P1_ANCHOR, 0, "SUBINDUSTRY"),
    # group_neutralize test
    ("p4_neut_si", "group_neutralize(ts_rank(%s, 252), subindustry)" % P1_ANCHOR, 3, "SUBINDUSTRY"),
    ("p4_neut_mkt", "group_neutralize(ts_rank(%s, 252), market)" % P1_ANCHOR, 3, "MARKET"),
    # GM_AVG densify (ultra-virgin field)
    ("p4_giavg_densify_d0", "group_rank(%s, densify(bucket(rank(cap), range='0.1,1,0.1')))" % GR_AVG, 0, "INDUSTRY"),
]

# ==============================================================
# Phase 5: SC Verification (runs later, after sims complete)
# ==============================================================

ALL_PHASES = [
    ("01_baseline", PHASE01, "Baseline confirmation — sign, group, best field"),
    ("02_smoothing", PHASE02, "Smoothing & ts_rank position"),
    ("03_alternative", PHASE03, "Alternative definitions"),
    ("04_upgrade", PHASE04, "Upgrade wrappers"),
]

ALL_VARIANTS = PHASE01 + PHASE02 + PHASE03 + PHASE04
print(f"Total variants planned: {len(ALL_VARIANTS)}", flush=True)

# ==============================================================
# Execution
# ==============================================================
def submit_wave(s, variants, wave_label):
    results = []
    print("\n" + "=" * 60, flush=True)
    print("  [%s] Submitting %d variants @ %s" % (wave_label, len(variants), datetime.now().isoformat()), flush=True)
    print("=" * 60, flush=True)

    for name, expr, decay, neut in variants:
        sim_data = {
            "type": "REGULAR",
            "settings": dict(BASE_SETTINGS, decay=decay, neutralization=neut),
            "regular": expr,
        }
        print("\n  ▶ %s..." % name, flush=True)
        resp = s.post("https://api.worldquantbrain.com/simulations", json=sim_data)
        if resp.status_code != 201:
            print("    ❌ HTTP %d: %s" % (resp.status_code, resp.text[:200]), flush=True)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", 300))
                print("    ⏳ Rate limited, waiting %ds..." % wait, flush=True)
                time.sleep(wait + 5)
                resp = s.post("https://api.worldquantbrain.com/simulations", json=sim_data)
                if resp.status_code != 201:
                    print("    ❌ Still failed after rate limit wait: %s" % resp.text[:100], flush=True)
                    continue
            else:
                continue

        poll_url = resp.headers.get("Location")
        if not poll_url:
            continue

        name_f = name
        for attempt in range(60):
            prog = s.get(poll_url)
            ra = prog.headers.get("Retry-After")
            if ra:
                time.sleep(float(ra))
                continue
            status = prog.json().get("status")
            alpha_id = prog.json().get("alpha")
            if status in ("COMPLETE", "WARNING") and alpha_id:
                ad = s.get("https://api.worldquantbrain.com/alphas/%s" % alpha_id).json()
                im = ad.get("is", {})
                sharpe = im.get("sharpe")
                fitness = im.get("fitness")
                turnover = im.get("turnover")
                margin = im.get("margin")
                print("    ✓ %s S=%.3f F=%.3f TVR=%.4f" % (name_f, sharpe, fitness, turnover), flush=True)
                results.append({
                    "alpha_id": alpha_id, "name": name_f, "expression": expr,
                    "sharpe": sharpe, "fitness": fitness, "turnover": turnover,
                    "margin": margin, "decay": decay, "neutralization": neut,
                    "longCount": im.get("longCount"), "shortCount": im.get("shortCount"),
                })
                break
            elif status == "ERROR":
                print("    ❌ %s ERROR" % name_f, flush=True)
                break
            time.sleep(5)
        else:
            print("    ⏰ %s timeout" % name_f, flush=True)

    return results

def main():
    print("=" * 70, flush=True)
    print("  Gross Profitability Premium — 24h Batch Mining", flush=True)
    print("  %s" % datetime.now().isoformat(), flush=True)
    print("=" * 70, flush=True)
    print("\n  Fields:", flush=True)
    print("    gross_income_reported_value (analyst4, 69.5%%, 184 alphas)", flush=True)
    print("    total_assets_amount (analyst4, 80.4%%, 158 alphas)", flush=True)
    print("    gross_income_max (analyst4, 68%%, 17 alphas — virgin)", flush=True)
    print("    gross_income_avg (analyst4, 68%%, 5 alphas — virgin)", flush=True)
    print("    anl4_gric_mean (analyst4, 60.3%%, 659 alphas)", flush=True)
    print("    fnd6_newa1v1300_gp (fundamental6, 50%%, 2599 alphas, fallback)", flush=True)
    print("\n  Variants: %d total" % len(ALL_VARIANTS), flush=True)
    print("  Phases: %d" % len(ALL_PHASES), flush=True)

    s = login()

    all_results = []
    phase_times = []

    for phase_key, variants, desc in ALL_PHASES:
        t0 = time.time()
        print("\n" + "#" * 60, flush=True)
        print("  Phase: %s — %s" % (phase_key, desc), flush=True)
        print("  Variants: %d" % len(variants), flush=True)
        print("#" * 60, flush=True)

        phase_results = submit_wave(s, variants, phase_key)
        elapsed = time.time() - t0
        all_results.extend(phase_results)
        phase_times.append({"phase": phase_key, "variants": len(variants), "passed": len(phase_results), "elapsed_s": round(elapsed, 1)})
        print("\n  Phase %s: %d/%d passed in %.1fs" % (phase_key, len(phase_results), len(variants), elapsed), flush=True)

        # Save intermediate after each phase
        intermediate = {
            "phase": phase_key,
            "elapsed_s": elapsed,
            "completed_at": datetime.now().isoformat(),
            "cumulative_phases": phase_times,
        }
        with open(OUTPUT_DIR / f"phase_{phase_key}_done.json", "w") as f:
            json.dump(intermediate, f, indent=2, default=str)

    # Save all results
    report = {
        "title": "Gross Profitability Premium — 24h Batch Mining Results",
        "generated_at": datetime.now().isoformat(),
        "total_variants": len(ALL_VARIANTS),
        "total_passed": len(all_results),
        "phases": phase_times,
        "results": sorted(all_results, key=lambda x: -(x.get("sharpe") or 0)),
    }
    with open(OUTPUT_DIR / f"gp_24h_results_{TIMESTAMP}.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Print summary
    print("\n" + "=" * 70, flush=True)
    print("  RESULTS SUMMARY", flush=True)
    print("=" * 70, flush=True)
    print("  Total variants: %d" % len(ALL_VARIANTS), flush=True)
    print("  Passed: %d (%.0f%%)" % (len(all_results), 100 * len(all_results) / max(len(ALL_VARIANTS), 1)), flush=True)

    if all_results:
        print("\n  Top 15 by Sharpe:", flush=True)
        ranked = sorted(all_results, key=lambda x: -(x.get("sharpe") or 0))
        for i, r in enumerate(ranked[:15]):
            print("  #%2d  %-12s  S=%.3f  F=%.3f  TVR=%.4f  [%s]" % (
                i+1, r["name"], r["sharpe"] or 0, r["fitness"] or 0,
                r["turnover"] or 0, r["alpha_id"]), flush=True)

        # S>=1.0 candidates
        strong = [r for r in all_results if (r.get("sharpe") or 0) >= 1.0]
        if strong:
            print("\n  S>=1.0 candidates: %d" % len(strong), flush=True)

    print("\n  Report: %s" % (OUTPUT_DIR / f"gp_24h_results_{TIMESTAMP}.json"), flush=True)
    print("=" * 70, flush=True)

    # Re-run info
    print("\n  To re-run SC check later:", flush=True)
    print("  python3 -c \"")
    print("    import json, time")
    print("    s = login()")
    print("    results = json.load(open('%s/gp_24h_results_%s.json'))['results']" % (OUTPUT_DIR, TIMESTAMP))
    print("    for r in results:")
    print("        if r['sharpe'] >= 1.25 and r['turnover'] < 0.6:")
    print("            rc = s.get('https://api.worldquantbrain.com/alphas/' + r['alpha_id'] + '/check')")
    print("            # parse SC result...")
    print("  \"", flush=True)

if __name__ == "__main__":
    main()
