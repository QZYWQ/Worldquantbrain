#!/usr/bin/env python3
"""Full account state sync — BRAIN API."""

import sys
import json
import time
from datetime import datetime
from pathlib import Path

from machine_lib import login

PROJECT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")

def log(msg):
    print(msg, flush=True)

def fetch_all(session):
    """Fetch all user alphas with pagination (API max limit=100)."""
    all_a = []
    offset = 0
    while True:
        resp = session.get(
            f"https://api.worldquantbrain.com/users/self/alphas"
            f"?limit=100&offset={offset}&hidden=false&type!=SUPER"
        )
        if resp.status_code != 200:
            log(f"  Fetch error at offset={offset}: HTTP {resp.status_code}")
            break
        data = resp.json()
        batch = data.get("results", [])
        all_a.extend(batch)
        log(f"  offset={offset}: got {len(batch)} (total {len(all_a)})")
        if len(batch) < 100:
            break
        offset += 100
        time.sleep(0.3)
    return all_a

def get_check(session, alpha_id):
    for _ in range(3):
        try:
            resp = session.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}/check")
            if resp.status_code == 200 and resp.text:
                return resp.json()
            wait = resp.headers.get("retry-after")
            time.sleep(float(wait) if wait else 3)
        except Exception:
            time.sleep(5)
    return None

def main():
    log(f"BRAIN Sync — {datetime.now().isoformat()}")
    log("=" * 60)
    s = login()

    log("\n[1/3] Fetching all alphas...")
    all_a = fetch_all(s)
    submitted = [a for a in all_a if a.get("status") == "ACTIVE"]
    unsubmitted = [a for a in all_a if a.get("status") == "UNSUBMITTED"]
    log(f"\n  Total: {len(all_a)} | ACTIVE: {len(submitted)} | UNSUBMITTED: {len(unsubmitted)}")

    log("\n[2/3] Analyzing unsubmitted...")
    candidates = []
    for a in unsubmitted:
        ism = a.get("is", {})
        s_ = ism.get("sharpe")
        if s_ and s_ > 0:
            candidates.append({
                "id": a["id"], "sharpe": s_, "fitness": ism.get("fitness"),
                "turnover": ism.get("turnover"),
                "decay": a.get("settings",{}).get("decay"),
                "neut": a.get("settings",{}).get("neutralization"),
            })
    candidates.sort(key=lambda x: x["sharpe"] or 0, reverse=True)
    log(f"  Positive: {len(candidates)} | S>=1.5: {sum(1 for c in candidates if c['sharpe']>=1.5)}")

    log("\n[3/3] Checking S>=1.0 candidates (with rate-limit protection)...")
    time.sleep(3)  # Warm-down before batch checks
    to_check = [c for c in candidates if c["sharpe"] >= 1.0][:30]
    checked = []
    for i, c in enumerate(to_check):
        r = get_check(s, c["id"])
        if r:
            checks = r.get("is",{}).get("checks",[])
            c["checks"] = {chk["name"]:{"result":chk["result"],"value":chk.get("value")} for chk in checks}
            c["all_pass"] = all(chk["result"]=="PASS" for chk in checks)
        else:
            c["checks"], c["all_pass"] = {}, False
        checked.append(c)
        if (i+1)%5==0:
            log(f"  {i+1}/{len(to_check)}")
        time.sleep(2.0)

    e8 = sorted([c for c in checked if c["all_pass"] and c["sharpe"]>=1.5],
                key=lambda x: x["sharpe"], reverse=True)
    e7 = sorted([c for c in checked if c["all_pass"] and 1.0<=c["sharpe"]<1.5],
                key=lambda x: x["sharpe"], reverse=True)
    near = sorted([c for c in checked if not c["all_pass"] and c["sharpe"]>=1.5],
                  key=lambda x: x["sharpe"], reverse=True)

    local_favs = set()
    for p in [PROJECT/"runs"/"simulation-captures"/"final-8pass-favorites.json",
              PROJECT/"runs"/"simulation-captures"/"new-account-final-ranking.json"]:
        if p.exists():
            try:
                d = json.loads(p.read_text())
                for item in d.get("favorites_marked",[])+d.get("eight_pass_candidates",[]):
                    local_favs.add(item.get("id") or item.get("alpha_id"))
            except: pass

    report = dict(synced_at=datetime.now().isoformat(), account="mcydedn@outlook.com",
        summary={"total": len(all_a), "active": len(submitted), "unsubmitted": len(unsubmitted),
                 "positive": len(candidates), "8pass": len(e8), "7pass": len(e7)},
        active=sorted([{"id":a["id"],"sharpe":a.get("is",{}).get("sharpe"),
                        "fitness":a.get("is",{}).get("fitness")} for a in submitted],
                      key=lambda x: x["sharpe"] or 0, reverse=True),
        eight_pass=e8, seven_pass=e7, near_pass=near,
        local_favorites=list(local_favs))

    out = PROJECT/"runs"/"simulation-captures"/f"account-sync-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, indent=2, default=str))

    log(f"\n{'='*60}")
    log(f"ACCOUNT: 738 | ACTIVE: {len(report['active'])} | 8-PASS: {len(e8)} | 7-PASS: {len(e7)}")
    log(f"{'='*60}")
    log(f"\n✅ ACTIVE (submitted):")
    for a in report["active"]:
        log(f"  {a['id']}: S={a['sharpe']} F={a['fitness']}")

    log(f"\n⭐ 8-PASS (S≥1.5):")
    for c in e8:
        sc = c.get("checks",{}).get("SELF_CORRELATION",{}).get("value","?")
        l = "⭐LOCAL" if c["id"] in local_favs else ""
        log(f"  {c['id']}: S={c['sharpe']:.2f} F={c['fitness']:.2f} TVR={c['turnover']:.4f} SC={sc} {l}")

    log(f"\n🔶 7-PASS (1.0≤S<1.5):")
    for c in e7:
        sc = c.get("checks",{}).get("SELF_CORRELATION",{}).get("value","?")
        l = "⭐LOCAL" if c["id"] in local_favs else ""
        log(f"  {c['id']}: S={c['sharpe']:.2f} F={c['fitness']:.2f} TVR={c['turnover']:.4f} SC={sc} {l}")

    log(f"\n🔴 Near-pass (S≥1.5 fail):")
    for c in near:
        fail = [k for k,v in c.get("checks",{}).items() if v.get("result")!="PASS"]
        log(f"  {c['id']}: S={c['sharpe']:.2f} F={c['fitness']:.2f} FAIL: {fail}")

    log(f"\n📁 {out}")

main()
