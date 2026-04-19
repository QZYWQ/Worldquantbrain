# Lower-Correlation Follow-up Minimum Plan

- Date: `2026-04-20`
- Primary constraint: keep `E5repQ81` locked while official OS remains unresolved
- Current branch posture: the `anl4_afv4_dts_spe` disagreement branch is now a weak diagnostic branch, not the next submission lane

## Recommended Next Lane

Prioritize a non-analyst branch next, starting from the existing `sentiment_buzz_stability` idea before the option-volume gate fallback.

Why this lane first:

- it is more structurally different from the submitted analyst EPS alpha
- it offers a clearer path to lower self-correlation than another analyst-family sibling
- the disagreement branch already failed the first cheap sign test, so another hour there has lower expected reward

## Minimum Execution Sequence

1. Re-verify one sentiment or buzz-style field on the official Data page in `USA / D1 / TOP3000`.
2. Write a field-search pack only after one concrete field is confirmed.
3. Draft one baseline plus three stability-window variants around the confirmed field.
4. Run a first four-simulation batch and capture only real platform metrics.
5. Create a candidate batch only if the new lane later exposes real submission-check evidence, including non-null `subuniverse_pass`.

## Fallback Rule

If no usable sentiment field is visible on the official Data page, switch the same minimum sequence to the existing `event_option_volume_gate` lane instead of returning to more analyst-level clones.
