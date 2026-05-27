#!/usr/bin/env python3
"""Mark confirmed 8-pass alphas as favorites using local + API data."""

import sys
import json
import time
from datetime import datetime
from pathlib import Path

from machine_lib import login

PROJECT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")

def load_local_eight_pass():
    """Extract all confirmed 8-pass alphas from local records."""
    confirmed = {}

    # Source 1: May 22 detailed check record
    p1 = PROJECT / "runs" / "submission-memos" / "2026-05-22-current-8pass-record.json"
    # Source 2: May 25 account sync
    p2 = PROJECT / "runs" / "simulation-captures" / "account-sync-20260525_175802.json"
    # Source 3: New account final ranking
    p3 = PROJECT / "runs" / "simulation-captures" / "new-account-final-ranking.json"
    # Source 4: Upgrade phase 1
    p4 = PROJECT / "runs" / "simulation-captures" / "upgrade_phase1.json"
    # Source 5: Final 8-pass favorites
    p5 = PROJECT / "runs" / "simulation-captures" / "final-8pass-favorites.json"

    # From source 1 - find all with strict_8pass=true in the records
    try:
        data = json.loads(p1.read_text())
        for rec in data.get("records", []):
            if rec.get("check", {}).get("strict_8pass") and rec.get("status") != "ACTIVE":
                aid = rec["alpha_id"]
                m = rec.get("metrics", {})
                confirmed[aid] = {
                    "sharpe": m.get("sharpe"),
                    "fitness": m.get("fitness"),
                    "turnover": m.get("turnover"),
                    "sc": rec.get("check", {}).get("self_correlation") or
                          next((c.get("value") for c in rec.get("check", {}).get("checks", [])
                                if c["name"] == "SELF_CORRELATION"), None),
                    "source": "local_check_May22"
                }
    except: pass

    # From source 2 - API sync /check results (filter for all_pass)
    try:
        data = json.loads(p2.read_text())
        for c in data.get("eight_pass", []):
            if c["id"] not in confirmed:
                confirmed[c["id"]] = {
                    "sharpe": c["sharpe"], "fitness": c["fitness"],
                    "turnover": c["turnover"],
                    "sc": c.get("checks", {}).get("SELF_CORRELATION", {}).get("value"),
                    "source": "api_sync"
                }
    except: pass

    # From source 3
    try:
        data = json.loads(p3.read_text())
        for c in data.get("eight_pass_candidates", []):
            aid = c["alpha_id"]
            if aid not in confirmed:
                confirmed[aid] = {
                    "sharpe": c["sharpe"], "fitness": c["fitness"],
                    "turnover": c["turnover"], "sc": c.get("selfcorr"),
                    "source": "local_ranking"
                }
    except: pass

    # From source 5
    try:
        data = json.loads(p5.read_text())
        for c in data.get("favorites_marked", []):
            aid = c["id"]
            if aid not in confirmed:
                confirmed[aid] = {
                    "sharpe": c["sharpe"], "fitness": c["fitness"],
                    "turnover": c.get("turnover"), "sc": c.get("sc"),
                    "source": "local_favorite"
                }
    except: pass

    return confirmed

def set_favorite(session, alpha_id, color="#FFD700"):
    for _ in range(3):
        resp = session.patch(
            f"https://api.worldquantbrain.com/alphas/{alpha_id}",
            json={"color": color, "tags": ["favorite"]}
        )
        if resp.status_code == 200:
            return True
        time.sleep(2)
    return False

def clear_favorite(session, alpha_id):
    for _ in range(3):
        resp = session.patch(
            f"https://api.worldquantbrain.com/alphas/{alpha_id}",
            json={"color": None, "tags": []}
        )
        if resp.status_code == 200:
            return True
        time.sleep(2)
    return False

def main():
    print(f"Favorite Marker — {datetime.now().isoformat()}", flush=True)
    print("="*60, flush=True)

    # Load local confirmed 8-pass
    confirmed = load_local_eight_pass()
    print(f"\n[1] Locally confirmed 8-pass: {len(confirmed)} alphas", flush=True)

    # Filter S>=1.5
    s15 = {k: v for k, v in confirmed.items() if v["sharpe"] and v["sharpe"] >= 1.5}
    print(f"    S>=1.5: {len(s15)}", flush=True)
    for aid, info in sorted(s15.items(), key=lambda x: x[1]["sharpe"], reverse=True):
        print(f"      {aid}: S={info['sharpe']:.2f} F={info['fitness']} TVR={info['turnover']} SC={info.get('sc')}", flush=True)

    s_below = {k: v for k, v in confirmed.items() if v["sharpe"] and v["sharpe"] < 1.5}
    print(f"    S<1.5: {len(s_below)} (not marked)", flush=True)

    # Login
    s = login()
    time.sleep(3)

    # Get current favorites from API
    print(f"\n[2] Fetching current platform favorites...", flush=True)
    current_favs = set()
    offset = 0
    while True:
        resp = s.get(f"https://api.worldquantbrain.com/users/self/alphas?limit=100&offset={offset}&hidden=false&type!=SUPER")
        if resp.status_code != 200:
            break
        for a in resp.json().get("results", []):
            if a.get("color") or "favorite" in a.get("tags", []):
                current_favs.add(a["id"])
        offset += 100
        time.sleep(1)
        if len(resp.json().get("results", [])) < 100:
            break
    print(f"    Currently favorited: {len(current_favs)} alphas", flush=True)

    # Clear favorites that are NOT in our S>=1.5 8-pass list
    to_clear = current_favs - set(s15.keys())
    if to_clear:
        print(f"\n[3] Clearing {len(to_clear)} non-8-pass favorites...", flush=True)
        for aid in sorted(to_clear):
            ok = clear_favorite(s, aid)
            print(f"    ✗ CLEAR {aid}: {'OK' if ok else 'FAIL'}", flush=True)
            time.sleep(2)
    else:
        print(f"\n[3] No favorites to clear.", flush=True)

    # Mark S>=1.5 8-pass alphas as favorites
    to_mark = set(s15.keys()) - current_favs
    if to_mark:
        print(f"\n[4] Marking {len(to_mark)} new 8-pass favorites...", flush=True)
        for aid in sorted(to_mark):
            info = s15[aid]
            ok = set_favorite(s, aid)
            marker = "✅" if ok else "❌"
            print(f"    {marker} {aid}: S={info['sharpe']:.2f} SC={info.get('sc')}", flush=True)
            time.sleep(2)
    else:
        print(f"\n[4] All S>=1.5 8-pass already favorited (or already marked).", flush=True)

    # Re-verify by re-marking existing ones to ensure consistency
    already_marked = set(s15.keys()) & current_favs
    if already_marked:
        print(f"\n[5] Re-verifying {len(already_marked)} already-marked favorites...", flush=True)
        for aid in sorted(already_marked):
            ok = set_favorite(s, aid)
            info = s15[aid]
            print(f"    ✓ {aid}: S={info['sharpe']:.2f} {'OK' if ok else 'FAIL'}", flush=True)
            time.sleep(1.5)

    print(f"\n{'='*60}", flush=True)
    print(f"FINAL: {len(s15)} S>=1.5 8-PASS favorites marked", flush=True)
    print(f"{'='*60}", flush=True)

    print(f"\n⭐ FAVORITED 8-PASS (S>=1.5):", flush=True)
    for aid, info in sorted(s15.items(), key=lambda x: x[1]["sharpe"], reverse=True):
        print(f"  {aid}: S={info['sharpe']:.2f} F={info['fitness']:.2f} TVR={info['turnover']:.4f} SC={info.get('sc', '?')}", flush=True)

    # Save final list
    result = {
        "synced_at": datetime.now().isoformat(),
        "confirmed_8pass": sorted(
            [{"id": k, **v} for k, v in confirmed.items() if v["sharpe"] and v["sharpe"] >= 1.5],
            key=lambda x: x["sharpe"], reverse=True
        ),
        "favorited_count": len(s15),
        "cleared_count": len(to_clear),
    }
    out = PROJECT / "runs" / "simulation-captures" / f"favorites-final-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(result, indent=2, default=str))
    print(f"\n📁 {out}", flush=True)

main()
