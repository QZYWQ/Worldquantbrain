# Forum Template Excerpts

This note is a project-local extraction from the 2026-04-22 support-forum crawl.
It is meant to separate reusable workflow rules from reusable alpha template families.

## Skill-Worthy Workflows

### Dataset evaluation / freshness

Observed in: `BRAIN TIPS - 6 ways to quickly evaluate a new dataset`

Useful skeleton:

```text
None neutralization + decay 0
datafield
datafield != 0 ? 1 : 0
ts_std_dev(datafield, N) != 0 ? 1 : 0
abs(datafield) > X
ts_median(datafield, 1000) > X
X < scale_down(datafield) && scale_down(datafield) < Y
```

What it gives you:

- coverage
- update frequency
- bounds
- distribution

### NaN handling / missingness

Observed in: `Demystifying Simulation Settings: NaN Handling`

Useful skeleton:

```text
NaN Handling = On
NaN Handling = Off
ts_backfill()
is_nan()
to_nan()
group_max(sales, industry)
```

What it gives you:

- coverage recovery
- explicit missing-value control
- awareness of ambiguity vs. fill-in

### Validation / overfitting

Observed in: `How can I use the test period to improve the OS performance of my Alpha?`

Useful skeleton:

```text
80/20 training / test split
compare train vs test
use multiple test periods
use rank tests and sub/super universe tests
```

What it gives you:

- overfitting detection
- OS robustness
- stable candidate ranking

### Neutralization discipline

Observed in: `The Hidden Risk Filter: How Statistical Neutralization Sharpens Your Signals`

Useful skeleton:

```text
statistical neutralization
orthogonal / PCA-style cleanup
factor bleed removal
```

What it gives you:

- less hidden common-factor exposure
- lower correlation / self-correlation risk

## KB-Worthy Template Families

### Price / volume short horizon

Observed in: price-volume examples, tutorial posts, and course work.

Representative skeletons:

```text
rank(ts_delta(close, 3))
ts_zscore(close - ts_max(high, 20), 10)
-clv * rank(volume)
rank(ts_rank(news_post_vwap, 5))
```

### Fundamental / slow ratio

Observed in: `Finding Alphas: Fundamental and Model Data` and course work.

Representative skeletons:

```text
group_rank(net_income_annual / cap, industry)
ts_rank(group_rank(net_income / market_cap, industry), 252)
ts_rank(group_rank(operating_income / sales, industry), 252)
rank(ts_mean(rp_css_earnings, 20))
```

### Event trigger / low turnover

Observed in: `How to record entry price and exit trade` and trade_when-related examples.

Representative skeletons:

```text
close_at_event = trade_when(event, close, -1)
alpha = trade_when(event, signal, abs(close - close_at_event) / close > 0.1)
trade_when(rank(buzz) > 0.9, rank(sentiment_momentum), -1)
```

### Options / volatility

Observed in: options tutorials and option-demand posts.

Representative skeletons:

```text
ts_regression(unitconvert(-scl12_buzz, "CSShare:1", "Unit[]"), volume, 250)
rank(ts_rank(options_field, 5))
```

### Sentiment / news attention

Observed in: news and social media examples.

Representative skeletons:

```text
rank(ts_mean(nws1_sentiment, 5))
rank(nws1_sentiment) - rank(ts_delay(nws1_sentiment, 1))
```

## How To Use This

- Keep the workflows above as `skill-candidate` material.
- Use the template families above as `kb-candidate` material.
- Keep one-off forum opinions and page-specific formula comments in the project layer until they prove reusable.
