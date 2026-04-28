# kq17QGe8 Candidate Follow-up

## Alpha

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 60)), 5), subindustry)
```

## Metrics

- sharpe: 1.32
- fitness: 0.94
- turnover: 0.1783
- margin: 0.001013
- drawdown: 0.0582
- returns: 0.0903

## Internal Decision

- candidate-screen pass: yes
- ready-to-submit: no

## Why It Passed Internal Screen

- fitness > 0.8
- sharpe > 1.25
- returns > 0
- margin > 0
- turnover controlled below 0.3

## Remaining Platform Blockers

- LOW_FITNESS=FAIL
- LOW_SUB_UNIVERSE_SHARPE=FAIL

## Research Hypothesis

Longer close-volume correlation window improved stability and turnover. Next validation should tune correlation window, decay smoothing, and neutralization group to improve platform fitness and sub-universe Sharpe.

## Second-Round Variants

- corr40
- corr90
- corr60_decay10

## Decision

Do not submit yet. Run second-round local variants first.

## Second-Round Results

Baseline V2 / `kq17QGe8`:

- sharpe: 1.32
- fitness: 0.94
- turnover: 0.1783
- margin: 0.001013
- returns: 0.0903
- platform blockers: LOW_FITNESS=FAIL, LOW_SUB_UNIVERSE_SHARPE=FAIL, SELF_CORRELATION=PENDING

### corr40

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 40)), 5), subindustry)
```

- alpha_id: gJRAMRP0
- status: COMPLETE
- sharpe: 1.10
- fitness: 0.68
- turnover: 0.1890
- margin: 0.000763
- drawdown: 0.0511
- returns: 0.0721
- platform blockers: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_SUB_UNIVERSE_SHARPE=FAIL, SELF_CORRELATION=PENDING
- decision: hopeful, but weaker than V2

### corr90

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 90)), 5), subindustry)
```

- alpha_id: QP2JVEMW
- status: COMPLETE
- sharpe: 1.24
- fitness: 0.89
- turnover: 0.1713
- margin: 0.001034
- drawdown: 0.0868
- returns: 0.0886
- platform blockers: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, SELF_CORRELATION=PENDING
- decision: robustness improvement because LOW_SUB_UNIVERSE_SHARPE cleared, but not stronger than V2

### corr60_decay10

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 60)), 10), subindustry)
```

- alpha_id: zqPMmOEG
- status: COMPLETE
- sharpe: 1.25
- fitness: 0.98
- turnover: 0.1388
- margin: 0.001220
- drawdown: 0.0620
- returns: 0.0846
- platform blockers: LOW_FITNESS=FAIL, LOW_SUB_UNIVERSE_SHARPE=FAIL, SELF_CORRELATION=PENDING
- decision: fitness and turnover improvement, but not a new lead because Sharpe is below V2

## Current Lead

V2 / `kq17QGe8` remains the lead candidate by the current rule because no second-round variant exceeded both V2 fitness and V2 Sharpe while keeping turnover below 0.3.

## Next Step

Keep V2 as the main branch. Preserve corr90 as the robustness reference because it cleared LOW_SUB_UNIVERSE_SHARPE. The next local round should test at most three variants around the intersection of V2 and corr90, such as neutralization group changes or moderate smoothing, before any submission memo is finalized.
