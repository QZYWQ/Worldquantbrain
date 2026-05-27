#!/usr/bin/env python3
"""Asset Turnover Efficiency — 24h Batch Mining (Phased Execution).

Phases:
  0: Field health diagnostics — verify field availability & coverage
  1: Baseline confirmation — sign, group, window
  2: Change rate / delta direction
  3: Asset definition replacement
  4: Composite & upgrade wrappers
  5: SC verification & submission ranking

Each phase is run sequentially. Progress is saved between phases.
"""

import sys

import json
import time
from datetime import datetime
from pathlib import Path
from machine_lib import login, set_alpha_properties

PROJECT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
RESULTS_DIR = PROJECT / "runs" / "simulation-captures"
OUTPUT_DIR = PROJECT / "runs" / "overnight-mining" / "2026-05-26-asset-turnover-24h"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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
    return "add(abs(%s), 1)" % x

# Pre-compute wrapped field strings
W_REV = ws("revenue")
W_ASST = ws("assets")
W_PPENT = ws("ppent")
W_ACUR = ws("assets_curr")
W_OI = ws("operating_income")
ADD_PPENT_ACUR = "add(%s, %s)" % (W_PPENT, W_ACUR)

# ---- Phase 0: Field Diagnostics ----
PHASE00 = [
    ("s0_raw_assets", W_ASST, 0, "NONE"),
    ("s0_raw_revenue", W_REV, 0, "NONE"),
    ("s0_raw_ppent", W_PPENT, 0, "NONE"),
    ("s0_raw_acur", W_ACUR, 0, "NONE"),
    ("s0_nz_assets", "%s != 0 ? 1 : 0" % W_ASST, 0, "NONE"),
    ("s0_nz_revenue", "%s != 0 ? 1 : 0" % W_REV, 0, "NONE"),
    ("s0_freq_assets", "ts_std_dev(%s, 252) != 0 ? 1 : 0" % W_ASST, 0, "NONE"),
    ("s0_freq_revenue", "ts_std_dev(%s, 252) != 0 ? 1 : 0" % W_REV, 0, "NONE"),
]

# ---- Phase 1: Baseline Confirmation ----
def ra():
    return "divide(%s, %s)" % (W_REV, sa(W_ASST))

P1_RA = ra()

PHASE01 = [
    ("p1_base_at_i126",
     "group_rank(%s, industry)" % P1_RA, 6, "INDUSTRY"),
    ("p1_base_at_i63",
     "group_rank(ts_mean(%s, 63), industry)" % P1_RA, 6, "INDUSTRY"),
    ("p1_base_at_i252",
     "group_rank(ts_mean(%s, 252), industry)" % P1_RA, 6, "INDUSTRY"),
    ("p1_base_at_flip",
     "-group_rank(%s, industry)" % P1_RA, 6, "INDUSTRY"),
    ("p1_base_at_subind",
     "group_rank(%s, subindustry)" % P1_RA, 6, "SUBINDUSTRY"),
    ("p1_base_at_market",
     "group_rank(%s, market)" % P1_RA, 6, "MARKET"),
    ("p1_base_at_rank", "rank(%s)" % P1_RA, 6, "MARKET"),
    ("p1_base_at_zscore",
     "group_rank(ts_zscore(%s, 252), industry)" % P1_RA, 6, "INDUSTRY"),
]

# ---- Phase 2: Change Rate / Delta ----
def ra_smoothed(window):
    return "ts_mean(%s, %d)" % (P1_RA, window)

def ra_delta(smooth_w=126, delta_w=63):
    return "ts_delta(%s, %d)" % (ra_smoothed(smooth_w), delta_w)

PHASE02 = [
    ("p2_dr_21_126",
     "group_rank(%s, industry)" % ra_delta(126, 63), 6, "INDUSTRY"),
    ("p2_dr_21_252",
     "group_rank(%s, industry)" % ra_delta(252, 63), 6, "INDUSTRY"),
    ("p2_dr_63_126",
     "group_rank(%s, industry)" % ra_delta(126, 21), 6, "INDUSTRY"),
    ("p2_dr_63_252",
     "group_rank(%s, industry)" % ra_delta(252, 21), 6, "INDUSTRY"),
    ("p2_dr_126_252",
     "group_rank(%s, industry)" % ra_delta(252, 126), 6, "INDUSTRY"),
    ("p2_dr_21_126_si",
     "group_rank(%s, subindustry)" % ra_delta(126, 63), 6, "SUBINDUSTRY"),
    ("p2_dr_zscore",
     "group_rank(ts_zscore(%s, 126), industry)" % ra_delta(126, 63), 6, "INDUSTRY"),
    ("p2_dr_flip",
     "-group_rank(%s, industry)" % ra_delta(126, 63), 6, "INDUSTRY"),
    # Revenue-only delta (control vs revenue_momentum)
    ("p2_dr_rev_21_252",
     "group_rank(ts_delta(%s, 21) / ts_mean(%s, 252), industry)" % (W_REV, W_REV), 6, "INDUSTRY"),
    # Revenue/ppent delta
    ("p2_dr_rppent",
     "group_rank(ts_delta(ts_mean(divide(%s, %s), 126), 63), industry)" % (W_REV, sa(W_PPENT)), 6, "INDUSTRY"),
    # Revenue/assets_curr delta
    ("p2_dr_rac",
     "group_rank(ts_delta(ts_mean(divide(%s, %s), 126), 63), industry)" % (W_REV, sa(W_ACUR)), 6, "INDUSTRY"),
    # Revenue/(ppent+assets_curr) delta
    ("p2_dr_roa",
     "group_rank(ts_delta(ts_mean(divide(%s, %s), 126), 63), industry)" % (W_REV, sa(ADD_PPENT_ACUR)), 6, "INDUSTRY"),
]

# ---- Phase 3: Asset Definition Replacement ----
def rppent():
    return "divide(%s, %s)" % (W_REV, sa(W_PPENT))

def rac():
    return "divide(%s, %s)" % (W_REV, sa(W_ACUR))

def roa():
    return "divide(%s, %s)" % (W_REV, sa(ADD_PPENT_ACUR))

PHASE03 = [
    ("p3_rppent_i", "group_rank(%s, industry)" % rppent(), 6, "INDUSTRY"),
    ("p3_rppent_si", "group_rank(%s, subindustry)" % rppent(), 6, "SUBINDUSTRY"),
    ("p3_rppent_delta",
     "group_rank(ts_delta(ts_mean(%s, 126), 63), industry)" % rppent(), 6, "INDUSTRY"),
    ("p3_rac_i", "group_rank(%s, industry)" % rac(), 6, "INDUSTRY"),
    ("p3_rac_si", "group_rank(%s, subindustry)" % rac(), 6, "SUBINDUSTRY"),
    ("p3_rac_delta",
     "group_rank(ts_delta(ts_mean(%s, 126), 63), industry)" % rac(), 6, "INDUSTRY"),
    ("p3_roa_i", "group_rank(%s, industry)" % roa(), 6, "INDUSTRY"),
    ("p3_roa_delta",
     "group_rank(ts_delta(ts_mean(%s, 126), 63), industry)" % roa(), 6, "INDUSTRY"),
]

# ---- Phase 4: Composite & Upgrade ----
P1_RA2 = ra()

def rw_oi():
    return "divide(%s, %s)" % (W_OI, sa(W_REV))

PHASE04 = [
    # DuPont composite: turnover + margin
    ("p4_dupont_60_40",
     "group_rank(0.6*ts_rank(%s, 252) + 0.4*ts_rank(%s, 252), industry)" % (P1_RA2, rw_oi()),
     6, "INDUSTRY"),
    ("p4_dupont_70_30",
     "group_rank(0.7*ts_rank(%s, 252) + 0.3*ts_rank(%s, 252), industry)" % (P1_RA2, rw_oi()),
     6, "INDUSTRY"),
    # Densify upgrade
    ("p4_densify_d0",
     "group_rank(%s, densify(bucket(rank(cap), range='0.1,1,0.1')))" % P1_RA2,
     0, "INDUSTRY"),
    ("p4_densify_d3",
     "group_rank(%s, densify(bucket(rank(cap), range='0.1,1,0.1')))" % P1_RA2,
     3, "INDUSTRY"),
    ("p4_densify_d6",
     "group_rank(%s, densify(bucket(rank(cap), range='0.1,1,0.1')))" % P1_RA2,
     6, "INDUSTRY"),
    # Delta with densify
    ("p4_densify_delta_d0",
     "group_rank(%s, densify(bucket(rank(cap), range='0.1,1,0.1')))" % ra_delta(126, 63),
     0, "INDUSTRY"),
    # Group neutralization
    ("p4_neut_at",
     "group_neutralize(ts_rank(%s, 252), industry)" % P1_RA2, 3, "INDUSTRY"),
    ("p4_neut_at_delta",
     "group_neutralize(ts_rank(%s, 126), industry)" % ra_delta(126, 63), 3, "INDUSTRY"),
]

# ---- Phase List ----
ALL_PHASES = [
    ("00_field_diagnostics", PHASE00, "Field health diagnostics"),
    ("01_baseline", PHASE01, "Baseline confirmation"),
    ("02_change_rate", PHASE02, "Change rate / delta direction"),
    ("03_asset_def", PHASE03, "Asset definition replacement"),
    ("04_composite", PHASE04, "Composite & upgrade wrappers"),
]

def submit_wave(s, variants, wave_label="wave"):
    """Submit a wave of variants, poll, and return results."""
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
                time.sleep(wait)
                resp = s.post("https://api.worldquantbrain.com/simulations", json=sim_data)
                if resp.status_code != 201:
                    results.append({"name": name, "status": "FAILED", "http": resp.status_code})
                    continue
            else:
                results.append({"name": name, "status": "FAILED", "http": resp.status_code})
                continue

        progress_url = resp.headers.get("Location")
        if not progress_url:
            results.append({"name": name, "status": "NO_LOCATION"})
            continue

        # Poll for completion
        for attempt in range(180):
            time.sleep(5)
            prog = s.get(progress_url)
            retry = prog.headers.get("Retry-After")
            if retry:
                time.sleep(float(retry))
                continue
            if prog.status_code != 200:
                if attempt % 12 == 0:
                    print("    ⏳ HTTP %d" % prog.status_code, flush=True)
                continue

            status = prog.json().get("status", "")
            if status in ("COMPLETE", "WARNING"):
                alpha_id = prog.json().get("alpha")
                if alpha_id:
                    try:
                        set_alpha_properties(
                            s, alpha_id,
                            name="at_" + name,
                            color="YELLOW",
                            tags=["asset_turnover_24h"],
                        )
                    except Exception:
                        pass
                    a_resp = s.get("https://api.worldquantbrain.com/alphas/%s" % alpha_id)
                    if a_resp.status_code == 200:
                        ad = a_resp.json()
                        ism = ad.get("is", {})
                        s_ = ism.get("sharpe")
                        f_ = ism.get("fitness")
                        t_ = ism.get("turnover")
                        print("    ✅ %s: S=%.2f F=%.2f TVR=%.4f" % (name, s_, f_, t_), flush=True)
                        results.append({
                            "name": name, "alpha_id": alpha_id,
                            "sharpe": s_, "fitness": f_, "turnover": t_,
                            "expression": expr, "decay": decay, "neutralization": neut,
                            "status": "COMPLETE",
                        })
                    else:
                        results.append({"name": name, "alpha_id": alpha_id, "status": "NO_METRICS"})
                break
            elif status in ("CANCELLED", "ERROR"):
                print("    ❌ %s: %s" % (name, status), flush=True)
                results.append({"name": name, "status": status})
                break
        else:
            print("    ❌ %s: TIMEOUT" % name, flush=True)
            results.append({"name": name, "status": "TIMEOUT"})

        # Rate limit spacing
        time.sleep(4)

    return results


def print_phase_summary(phase_name, results):
    passes = [r for r in results if r.get("sharpe") is not None]
    print("\n" + "=" * 60, flush=True)
    print("  [%s] Summary" % phase_name, flush=True)
    print("=" * 60, flush=True)
    print("  Completed: %d / %d" % (len(passes), len(results)), flush=True)
    print("  Fails: %d" % len([r for r in results if r.get("sharpe") is None]), flush=True)
    if passes:
        passes_sorted = sorted(passes, key=lambda x: x.get("sharpe", 0), reverse=True)
        print("\n  Top candidates (by Sharpe):", flush=True)
        for r in passes_sorted[:5]:
            print("    %s: S=%.2f F=%.2f TVR=%.4f" % (r["name"], r.get("sharpe", 0), r.get("fitness", 0), r.get("turnover", 0)), flush=True)


def main():
    start_time = datetime.now()
    print("Asset Turnover Efficiency — 24h Batch Mining", flush=True)
    print("Started: %s" % start_time.isoformat(), flush=True)
    print("Total phases: %d" % len(ALL_PHASES), flush=True)
    total_variants = sum(len(v) for _, v, _ in ALL_PHASES)
    print("Total variants: %d" % total_variants, flush=True)

    s = login()
    all_results = {}

    for phase_key, variants, description in ALL_PHASES:
        print("\n" + "#" * 60, flush=True)
        print("  PHASE %s: %s" % (phase_key, description), flush=True)
        print("  Variants: %d" % len(variants), flush=True)
        print("#" * 60, flush=True)

        phase_results = submit_wave(s, variants, wave_label=phase_key)
        all_results[phase_key] = phase_results
        print_phase_summary(phase_key, phase_results)

        # Save intermediate
        report = {
            "phase": phase_key,
            "description": description,
            "started_at": start_time.isoformat(),
            "phase_completed_at": datetime.now().isoformat(),
            "results": phase_results,
        }
        out_file = RESULTS_DIR / ("asset-turnover-%s-%s.json" % (phase_key, start_time.strftime("%Y%m%d_%H%M%S")))
        out_file.write_text(json.dumps(report, indent=2, default=str))
        print("\n  Saved: %s" % out_file, flush=True)

        # Kill check: Phase 1 max Sharpe < 0.5
        if phase_key == "01_baseline":
            max_s = max((r.get("sharpe", 0) or 0) for r in phase_results)
            if max_s < 0.5:
                print("\n  ❌ KILL: Phase 1 max Sharpe %.2f < 0.5. Stopping." % max_s, flush=True)
                break

    # ---- Final Report ----
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 60, flush=True)
    print("  FINAL REPORT", flush=True)
    print("  Duration: %.1fh" % (duration / 3600), flush=True)
    print("  Phases executed: %d" % len([k for k in all_results if all_results[k]]), flush=True)
    print("=" * 60, flush=True)

    all_passes = []
    for phase_key, results in all_results.items():
        for r in results:
            if r.get("sharpe") is not None:
                all_passes.append(dict(r, phase=phase_key))

    if all_passes:
        all_passes.sort(key=lambda x: x.get("sharpe", 0), reverse=True)
        print("\n  Total passing candidates: %d" % len(all_passes), flush=True)
        print("\n  Top 10 overall:", flush=True)
        print("  %-6s %-25s %-8s %-8s %-8s %-12s" % ("Rank", "Name", "S", "F", "TVR", "Phase"), flush=True)
        print("  %-6s %-25s %-8s %-8s %-8s %-12s" % ("-"*6, "-"*25, "-"*8, "-"*8, "-"*8, "-"*12), flush=True)
        for i, r in enumerate(all_passes[:10]):
            print("  %-6d %-25s %-8.2f %-8.2f %-8.4f %-12s" % (i+1, r["name"], r.get("sharpe", 0), r.get("fitness", 0), r.get("turnover", 0), r["phase"]), flush=True)

    final_report = {
        "started_at": start_time.isoformat(),
        "ended_at": end_time.isoformat(),
        "duration_hours": duration / 3600,
        "phases": {k: v for k, v in all_results.items() if v},
        "top_candidates": all_passes[:20] if all_passes else [],
    }
    final_out = OUTPUT_DIR / ("batch-results-%s.json" % start_time.strftime("%Y%m%d_%H%M%S"))
    final_out.write_text(json.dumps(final_report, indent=2, default=str))
    print("\n  Final report: %s" % final_out, flush=True)
    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
