#!/usr/bin/env python3
"""Sync favorites: mark new 8-pass GP alphas, verify existing, remove stale.

Uses machine_lib from integrated pipeline.
"""
import json, time
from pathlib import Path
from datetime import datetime
from machine_lib import login

OUT = Path("/Users/zpdedn/Documents/project/Worldquantbrain/runs/submission-memos")

s = login()

# ============================================================
# STEP 1: Mark new 8-pass GP candidates
# ============================================================
NEW_8PASS = [
    ("Jjbd6OOO", "gp_fb_d189_d6", 1.540, 1.090, 0.0324, 0.880, 0.6502),
    ("88nzmOpv", "gp_fb_gimax_d252", 1.460, 1.060, 0.0227, 0.950, 0.6866),
]

print("=" * 70, flush=True)
print("STEP 1: Mark new 8-pass GP candidates as favorites", flush=True)
print("=" * 70, flush=True)

for aid, name, sh, fi, tvr, subu, sc in NEW_8PASS:
    r = s.patch(f"https://api.worldquantbrain.com/alphas/{aid}", json={
        "color": "YELLOW", "tags": ["favorite", "gp_24h"], "favorite": True
    })
    if r.status_code in (200, 204):
        print(f"  ✓ {name} ({aid}) → marked YELLOW favorite", flush=True)
    else:
        print(f"  ✗ {name} ({aid}) → HTTP {r.status_code}", flush=True)
    time.sleep(1)

# ============================================================
# STEP 2: Get ALL favorites and verify them
# ============================================================
print("\n" + "=" * 70, flush=True)
print("STEP 2: Fetch all favorites from account", flush=True)
print("=" * 70, flush=True)

all_favs = []
for offset in range(0, 500, 100):
    url = f"https://api.worldquantbrain.com/users/self/alphas?limit=100&offset={offset}&hidden=false&type!=SUPER&order=-is.sharpe"
    r = s.get(url)
    if r.status_code != 200: break
    for a in r.json().get("results", []):
        if a.get("favorite") or a.get("color"):
            aid = a["id"]; sh = a["is"]["sharpe"]; fi = a["is"]["fitness"]
            tvr = a["is"]["turnover"]
            all_favs.append({
                "alpha_id": aid, "sharpe": sh, "fitness": fi, "turnover": tvr,
                "favorite": a.get("favorite"), "color": a.get("color"),
                "tags": a.get("tags", []),
                "expr": a.get("regular", {}).get("code","")[:80] if isinstance(a.get("regular"), dict) else "",
            })
    if len(r.json().get("results", [])) < 100: break
    time.sleep(0.5)

true_favs = [f for f in all_favs if f["favorite"] == True]
colored = [f for f in all_favs if f["favorite"] != True and f["color"]]

print(f"Total colored/stared: {len(all_favs)}", flush=True)
print(f"True favorites (fav=true): {len(true_favs)}", flush=True)
print(f"Colored only: {len(colored)}", flush=True)

# ============================================================
# STEP 3: Check true favorites — verify 8-pass status
# ============================================================
print("\n" + "=" * 70, flush=True)
print("STEP 3: Verify all true favorites still pass checks", flush=True)
print("=" * 70, flush=True)

verified_ok = []
to_remove = []

for fav in true_favs:
    aid = fav["alpha_id"]
    sh = fav["sharpe"]
    print(f"  ▶ {aid} S={sh:.3f}...", end=" ", flush=True)

    # /check
    rc = s.get(f"https://api.worldquantbrain.com/alphas/{aid}/check")
    if rc.status_code != 200:
        print(f"HTTP {rc.status_code} → KEEP (can't verify)", flush=True)
        verified_ok.append(fav)
        continue
    try:
        data = rc.json()
        checks = data.get("is", {}).get("checks", [])
        if not checks:
            print("PENDING → KEEP", flush=True)
            verified_ok.append(fav)
            continue
        fails = [c["name"] for c in checks if c["result"] == "FAIL"]
        sc_val = None
        for c in checks:
            if c["name"] == "SELF_CORRELATION":
                sc_val = c.get("value")
        sc_str = f"{sc_val:.4f}" if sc_val else "?"

        if fails:
            # Check if submitted (already ACTIVE)
            ad = s.get(f"https://api.worldquantbrain.com/alphas/{aid}").json()
            status = ad.get("status", "")
            if status in ("ACTIVE", "SUBMITTED"):
                print(f"✓ ACTIVE/SUBMITTED → KEEP", flush=True)
                verified_ok.append(fav)
            else:
                print(f"✗ FAILS={fails} SC={sc_str} → REMOVE favorite", flush=True)
                to_remove.append(fav)
        else:
            print(f"✓ ALL PASS SC={sc_str} → KEEP", flush=True)
            verified_ok.append(fav)
    except:
        print(f"PARSE ERROR → KEEP", flush=True)
        verified_ok.append(fav)

    time.sleep(2)

# ============================================================
# STEP 4: Remove stale favorites
# ============================================================
print(f"\nTo remove (stale): {len(to_remove)}", flush=True)
if to_remove:
    print("Removing favorites from stale alphas:", flush=True)
    for fav in to_remove:
        print(f"  ▶ {fav['alpha_id']} S={fav['sharpe']:.2f}...", end=" ", flush=True)
        r = s.patch(f"https://api.worldquantbrain.com/alphas/{fav['alpha_id']}", json={
            "favorite": False, "color": None, "tags": []
        })
        if r.status_code in (200, 204):
            print("removed", flush=True)
        else:
            print(f"HTTP {r.status_code}", flush=True)
        time.sleep(1)

# ============================================================
# STEP 5: Save aligned state
# ============================================================
print("\n" + "=" * 70, flush=True)
print("STEP 5: Save aligned favorites state", flush=True)
print("=" * 70, flush=True)

final_favs = []
for offset in range(0, 500, 100):
    url = f"https://api.worldquantbrain.com/users/self/alphas?limit=100&offset={offset}&hidden=false&type!=SUPER&order=-is.sharpe"
    r = s.get(url)
    if r.status_code != 200: break
    for a in r.json().get("results", []):
        if a.get("favorite") == True:
            aid = a["id"]; sh = a["is"]["sharpe"]; fi = a["is"]["fitness"]
            tvr = a["is"]["turnover"]
            expr = a.get("regular",{}).get("code","")[:80] if isinstance(a.get("regular"), dict) else ""
            final_favs.append({"alpha_id": aid, "sharpe": sh, "fitness": fi, "turnover": tvr, "expression": expr})
    if len(r.json().get("results",[])) < 100: break
    time.sleep(0.5)

# Print final list
print(f"\nFinal true favorites: {len(final_favs)}", flush=True)
print(f"{'AlphaID':<12} {'Sharpe':<8} {'Fitness':<8} {'TVR':<8} {'Expression':<40}", flush=True)
print("-" * 80, flush=True)
for f in sorted(final_favs, key=lambda x: -x.get("sharpe",0)):
    print(f'{f["alpha_id"]:<12} {f["sharpe"]:<8.3f} {f["fitness"]:<8.3f} {f["turnover"]:<8.4f} {f["expression"][:40]:<40}', flush=True)

# Save to local file
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
report = {
    "generated_at": ts,
    "summary": {
        "total_favorites_before": len(true_favs),
        "new_gp_favorites_added": len(NEW_8PASS),
        "stale_favorites_removed": len(to_remove),
        "total_favorites_after": len(final_favs),
    },
    "final_favorites": final_favs,
    "removed": [{"alpha_id": f["alpha_id"], "sharpe": f["sharpe"], "reason": "check_failed"} for f in to_remove],
}
path = OUT / f"favorites_synced_{ts}.json"
with open(str(path), "w") as f:
    json.dump(report, f, indent=2, default=str)
print(f"\nSaved: {path}", flush=True)
print("Done.", flush=True)
