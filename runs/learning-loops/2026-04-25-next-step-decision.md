# 2026-04-25 Next Step Decision

## Current State

- `qMmpvp8v` remains submitted and locked.
- `E5repQ81` remains the live OS reference alpha only; do not touch it.
- `pcr_vol_90` is frozen after batch 01.
- `pcr_oi_30` is frozen after batch 01.
- No submit-ready alpha exists in the current working queue.

## Best Next Move

Verify `pcr_oi_720` on the official Data Explorer page and only spend a minimal first batch there if it clears the front-door gate.

## Why This Beats The Alternatives

- `pcr_vol_90` never cleared the continuation floor: the best IS control stayed low-Fitness and the sign flip only mirrored the same edge.
- `pcr_oi_30` kept a modestly positive IS baseline, but TEST stayed weak and the 360d sibling turned negative on TEST.
- Reopening either frozen lane would be cosmetic.
- The next move should be a new family source, not another tenor polish pass.

## Ranked Queue

1. `pcr_oi_720` after fresh official field verification.
2. No more budget on `pcr_vol_90` or `pcr_oi_30`.

## Stop Rules

- Do not reopen `pcr_vol_90` or `pcr_oi_30` with sign flips, lookback swaps, smoothing, or group tweaks.
- Keep `qMmpvp8v` and `E5repQ81` untouched.
- If `pcr_oi_720` fails the front-door gate, rotate again instead of polishing.

## Source Trace

- `runs/submission-memos/2026-04-25-pcr-vol-90-live-first-batch.md`
- `runs/submission-memos/2026-04-25-pcr-vol-90-stop-memo.md`
- `runs/submission-memos/2026-04-25-pcr-oi-30-live-first-batch.md`
- `runs/submission-memos/2026-04-25-pcr-oi-30-stop-memo.md`
- Official API alpha URLs:
  - `https://api.worldquantbrain.com/alphas/58qKX001`
  - `https://api.worldquantbrain.com/alphas/zqJ7Vo6G`
  - `https://api.worldquantbrain.com/alphas/O05d37wp`
  - `https://api.worldquantbrain.com/alphas/xAmLKnpJ`
  - `https://api.worldquantbrain.com/alphas/N15dxPEq`
  - `https://api.worldquantbrain.com/alphas/58qmxR6k`
  - `https://api.worldquantbrain.com/alphas/gJol6AkQ`
  - `https://api.worldquantbrain.com/alphas/WjWZMwJx`
- Official field pages:
  - `https://platform.worldquantbrain.com/data/data-fields/pcr_vol_90?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`
  - `https://platform.worldquantbrain.com/data/data-fields/pcr_oi_30?delay=1&instrumentType=EQUITY&region=USA&universe=TOP3000`

## Next Trigger

Re-check only when fresh official evidence changes one of these states:

- `qMmpvp8v` resolves from `4 PENDING` to a final OS outcome
- `E5repQ81` resolves from `4 PENDING` to a final OS outcome
- `pcr_oi_720` clears its own official field verification and first minimal batch
