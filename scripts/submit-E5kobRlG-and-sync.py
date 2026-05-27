#!/usr/bin/env python3
"""Submit best starred favorite, unfavorite it, sync state, then run upgrade."""
import sys, json, time
from datetime import datetime
from pathlib import Path

from machine_lib import login

PROJECT = Path("/Users/zpdedn/Documents/project/Worldquantbrain")
OUT = PROJECT / "runs" / "submission-memos"
OUT.mkdir(parents=True, exist_ok=True)

TARGET = "E5kobRlG"

s = login()

# === Step 1: Run /check ===
print(f"\n=== Step 1: /check {TARGET} ===", flush=True)
resp = s.get(f"https://api.worldquantbrain.com/alphas/{TARGET}/check")
deadline = time.time() + 180
all_pass = False
sc_val = None
while time.time() < deadline:
    resp = s.get(f"https://api.worldquantbrain.com/alphas/{TARGET}/check")
    retry = resp.headers.get("retry-after")
    if retry: time.sleep(float(retry)); continue
    if resp.status_code != 200: time.sleep(5); continue
    try: data = resp.json()
    except: time.sleep(5); continue
    checks = data.get("is", {}).get("checks", [])
    if not checks: time.sleep(5); continue
    sc = next((c for c in checks if c["name"] == "SELF_CORRELATION"), None)
    sc_val = sc.get("value") if sc else None
    all_pass = all(c["result"] == "PASS" for c in checks)
    for c in checks:
        sym = "✅" if c["result"] == "PASS" else "❌"
        print(f"  {sym} {c['name']}: {c['result']} (value={c.get('value')})", flush=True)
    if sc and sc["result"] != "PENDING": break
    time.sleep(5)

if not all_pass:
    print(f"❌ {TARGET} not 8-pass, aborting", flush=True)
    sys.exit(1)
print(f"  ✅ {TARGET} 8-PASS SC={sc_val}", flush=True)

# === Step 2: Submit ===
print(f"\n=== Step 2: Submit {TARGET} ===", flush=True)
resp = s.post(f"https://api.worldquantbrain.com/alphas/{TARGET}/submit")
print(f"  HTTP {resp.status_code}: {resp.text[:200]}", flush=True)
time.sleep(3)

# Verify
r = s.get(f"https://api.worldquantbrain.com/alphas/{TARGET}")
if r.status_code == 200:
    status = r.json().get("status")
    print(f"  Post-submit status: {status}", flush=True)

# === Step 3: Remove favorite star ===
print(f"\n=== Step 3: Remove star from {TARGET} ===", flush=True)
# First check current state
r = s.get(f"https://api.worldquantbrain.com/alphas/{TARGET}")
if r.status_code == 200:
    ad = r.json()
    print(f"  Before: favorite={ad.get('favorite')} color={ad.get('color')} tags={ad.get('tags')}", flush=True)

# Unfavorite - set favorite=false, remove YELLOW color
resp = s.patch(f"https://api.worldquantbrain.com/alphas/{TARGET}", json={
    "favorite": False,
    "color": None,
    "tags": []
})
print(f"  Unfavorite PATCH: HTTP {resp.status_code}", flush=True)
time.sleep(2)

# Verify
r = s.get(f"https://api.worldquantbrain.com/alphas/{TARGET}")
if r.status_code == 200:
    ad = r.json()
    print(f"  After: favorite={ad.get('favorite')} color={ad.get('color')} tags={ad.get('tags')}", flush=True)

# === Step 4: Sync account state ===
print(f"\n=== Step 4: Sync account state ===", flush=True)
all_a = []
for offset in range(0, 2000, 100):
    r = s.get(f"https://api.worldquantbrain.com/users/self/alphas?limit=100&offset={offset}&hidden=false&type!=SUPER&order=-is.sharpe")
    if r.status_code != 200: break
    data = r.json()
    batch = data.get("results", [])
    all_a.extend(batch)
    if len(batch) < 100: break
    time.sleep(0.3)

submitted = [a for a in all_a if a.get("status") == "ACTIVE"]
favs = [a for a in all_a if a.get("favorite") == True]
print(f"  Total: {len(all_a)}", flush=True)
print(f"  Active: {len(submitted)}", flush=True)
for a in submitted:
    print(f"    ✅ {a['id']} S={a.get('is',{}).get('sharpe')}", flush=True)
print(f"  Starred favorites remaining: {len(favs)}", flush=True)
for a in favs:
    print(f"    ⭐ {a['id']} S={a.get('is',{}).get('sharpe')}", flush=True)

# Save canonical state
state = {
    "synced_at": datetime.now().isoformat(),
    "total": len(all_a),
    "active_submitted": len(submitted),
    "submitted_ids": [a["id"] for a in submitted],
    "starred_favorites_remaining": len(favs),
    "starred_favorites": [{"id": a["id"], "sharpe": a.get("is",{}).get("sharpe"), "fitness": a.get("is",{}).get("fitness")} for a in favs],
}
out_path = OUT / f"state-after-E5kobRlG-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
out_path.write_text(json.dumps(state, indent=2, default=str))
print(f"\n  Saved: {out_path}", flush=True)
