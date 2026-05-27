# Revenue Momentum SUS Lesson

## Source
2026-05-25 revenue_momentum batch（blvoqbPm: S=1.76, F=1.35, TVR=0.159, SUS=0.62 < 0.76)

## Decision: CANNOT SUBMIT
SUS=0.62 FAIL against 0.76 limit. Not close enough for a targeted rescue.

## Root Cause: Revenue Concentration
Revenue (top-line) is structurally more concentrated by market cap than operating_income. The densify(bucket(rank(cap))) wrapper that rescued operating_income (S=1.65→2.07, SUS pass at 0.8081) only lifted revenue_momentum SUS from ~0.57 to 0.62 — still below the 0.76 threshold.

Compare:
- VkOY2jWY: operating_income + densify → S=2.07, SUS PASS ✅
- blvoqbPm: revenue_delta + densify → S=1.76, SUS FAIL ❌

## Why
Revenue is highly correlated with market cap (large caps have proportionally large revenue). The densify wrapper partitions by cap but the within-bucket revenue ranking still tracks cap too closely. Operating income has more cross-sectional variance independent of size and responds better to densify.

## Applied Lesson
- **Revenue-based signals → SUS is the first bottleneck**, not Sharpe or Fitness
- Operating income is structurally superior for densify upgrades because it has more size-independent variance
- For revenue signals, consider alternative SUS strategies: industry/subindustry neutralization, more extreme winsorize, or accept as non-submittable

## Status
Family: revenue_momentum → moved to hold. Not worth more 24h budget on SUS rescue for revenue-based signals.
Best candidate blvoqbPm preserved for reference, not for polishing.
