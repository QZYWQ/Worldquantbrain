#!/usr/bin/env python3
"""Check all S>=1.5 alphas, mark true 8-pass as favorites."""

import sys
import json
import time
from datetime import datetime
from pathlib import Path

from machine_lib import login

PROJECT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")

def fetch_all(session):
    all_a = []
    offset = 0
    while True:
        resp = session.get(
            f"https://api.worldquantbrain.com/users/self/alphas"
            f"?limit=100&offset={offset}&hidden=false&type!=SUPER"
        )
        if resp.status_code != 200:
            break
        data = resp.json()
        batch = data.get("results", [])
        all_a.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return all_a

def get_check(session, alpha_id):
    for _ in range(5):
        try:
            resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}/check")
            if resp.status_code == 200 and resp.text.strip():
                return resp.json()
            wait = resp.headers.get("retry-after")
            time.sleep(float(wait) if wait else 5)
        except:
            time.sleep(5)
    return None

def parse_checks(result):
    if not result:
        return {}, False
    checks = result.get("is", {}).get("checks", [])
    check_map = {}
    all_pass = True
    for c in checks:
        name = c["name"]
        res = c["result"]
        val = c.get("value")
        check_map[name] = {"result": res, "value": val}
        if res != "PASS":
            all_pass = False
    return check_map, all_pass

def set_favorite(session, alpha_id, color="#FFD700"):
    """Mark alpha as favorite by setting color (gold = favorite)."""
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
    """Remove favorite mark."""
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
    print(f"Check & Favorite — {datetime.now().isoformat()}", flush=True)
    print("="*60, flush=True)

    s = login()

    # Fetch all
    print("\n[1/3] Fetching alphas...", flush=True)
    all_a = fetch_all(s)

    unsubmitted = [a for a in all_a if a.get("status") == "UNSUBMITTED"]

    # Collect S>=1.5
    candidates = []
    for a in unsubmitted:
        ism = a.get("is", {})
        s_ = ism.get("sharpe")
        f_ = ism.get("fitness")
        if s_ and s_ >= 1.5:
            candidates.append({
                "id": a["id"],
                "sharpe": s_,
                "fitness": f_,
                "turnover": ism.get("turnover"),
                "decay": a.get("settings", {}).get("decay"),
                "neut": a.get("settings", {}).get("neutralization"),
            })
    candidates.sort(key=lambda x: x["sharpe"], reverse=True)
    print(f"  S>=1.5 candidates: {len(candidates)}", flush=True)

    # Check all
    print(f"\n[2/3] Checking all {len(candidates)} candidates...", flush=True)
    results = []
    eight_pass = []
    for i, c in enumerate(candidates):
        r = get_check(s, c["id"])
        cm, ap = parse_checks(r)
        c["checks"] = cm
        c["all_pass"] = ap
        results.append(c)
        if ap:
            eight_pass.append(c)
        if (i+1) % 10 == 0:
            print(f"  {i+1}/{len(candidates)} checked | 8-PASS so far: {len(eight_pass)}", flush=True)
        time.sleep(2.0)

    # Current favorites - check what alphas currently have color
    print("\n[2b/3] Checking current favorites...", flush=True)
    current_favs = set()
    for a in all_a:
        color = a.get("color")
        tags = a.get("tags", [])
        if color or "favorite" in tags:
            current_favs.add(a["id"])
    print(f"  Currently favorited: {len(current_favs)}", flush=True)

    # Mark favorites
    print(f"\n[3/3] Updating favorites...", flush=True)
    eight_pass_ids = {c["id"] for c in eight_pass}

    # Clear favorites that are no longer 8-pass
    to_clear = current_favs - eight_pass_ids
    for aid in to_clear:
        ok = clear_favorite(s, aid)
        print(f"  ✗ UNMARK {aid}: {'OK' if ok else 'FAIL'}", flush=True)
        time.sleep(1.0)

    # Mark new 8-pass as favorites
    to_mark = eight_pass_ids - current_favs
    for c in eight_pass:
        if c["id"] in to_mark or True:  # Re-mark all to ensure consistency
            ok = set_favorite(s, c["id"])
            sc = c["checks"].get("SELF_CORRELATION", {}).get("value", "?")
            marker = "⭐ NEW" if c["id"] in to_mark else "✓"
            print(f"  {marker} FAV {c['id']}: S={c['sharpe']:.2f} F={c['fitness']:.2f} SC={sc}", flush=True)
            time.sleep(1.0)

    # Build report
    # Clear non-8-pass favorites (in case any had favorite tag)
    print(f"\n[3b/3] Ensuring non-8-pass are NOT favorited...", flush=True)
    eight_pass_set = {c["id"] for c in eight_pass}
    for a in all_a:
        aid = a["id"]
        if aid in eight_pass_set:
            continue
        color = a.get("color")
        tags = a.get("tags", [])
        if color or "favorite" in tags:
            ok = clear_favorite(s, aid)
            print(f"  ✗ CLEAR {aid}: previous favorite, now removed", flush=True)
            time.sleep(0.5)

    report = {
        "synced_at": datetime.now().isoformat(),
        "total_s_ge_1.5_checked": len(candidates),
        "eight_pass_count": len(eight_pass),
        "eight_pass": [{
            "id": c["id"],
            "sharpe": c["sharpe"],
            "fitness": c["fitness"],
            "turnover": c["turnover"],
            "decay": c["decay"],
            "neut": c["neut"],
            "checks": {k: v for k, v in c["checks"].items() if k != "MATCHES_COMPETITION"},
            "all_pass": True,
        } for c in eight_pass],
        "all_results": [{
            "id": c["id"],
            "sharpe": c["sharpe"],
            "fitness": c["fitness"],
            "turnover": c["turnover"],
            "all_pass": c["all_pass"],
            "failing_checks": [k for k, v in c["checks"].items() if v.get("result") != "PASS"],
        } for c in results],
    }

    out = PROJECT / "runs" / "simulation-captures" / f"check-results-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, indent=2, default=str))

    print(f"\n{'='*60}", flush=True)
    print(f"RESULTS: {len(eight_pass)} 8-PASS out of {len(candidates)} checked", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"\n⭐ 8-PASS favorites marked:", flush=True)
    for c in eight_pass:
        sc = c["checks"].get("SELF_CORRELATION", {}).get("value", "?")
        print(f"  {c['id']}: S={c['sharpe']:.2f} F={c['fitness']:.2f} TVR={c['turnover']:.4f} SC={sc}", flush=True)

    s_fail = [c for c in results if not c["all_pass"] and c["sharpe"] >= 1.5]
    print(f"\n✗ Near-miss (S>=1.5 but check fail): {len(s_fail)}", flush=True)

    print(f"\n📁 {out}", flush=True)
    return report

main()
