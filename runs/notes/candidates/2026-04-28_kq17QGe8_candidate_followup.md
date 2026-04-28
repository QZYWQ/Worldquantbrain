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

## Third-Round Results

Baseline V2 / `kq17QGe8` remains the comparison point:

- sharpe: 1.32
- fitness: 0.94
- turnover: 0.1783
- margin: 0.001013
- returns: 0.0903
- platform blockers: LOW_FITNESS=FAIL, LOW_SUB_UNIVERSE_SHARPE=FAIL

### corr90_decay10_subindustry

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 90)), 10), subindustry)
```

- fingerprint: e1964b75c6230df7ca1d5fd60e96ad07
- simulation status: COMPLETE
- alpha_id: Vk297b7Y
- sharpe: 1.15
- fitness: 0.90
- turnover: 0.1322
- margin: 0.001234
- drawdown: 0.0880
- returns: 0.0816
- grade: INFERIOR
- platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, SELF_CORRELATION=PENDING
- hopeful: yes
- internal candidate: no
- comparison against V2: lower Sharpe and fitness, lower turnover, cleared LOW_SUB_UNIVERSE_SHARPE
- decision: robustness reference, not a new lead

### corr90_decay20_subindustry

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 90)), 20), subindustry)
```

- fingerprint: 8d1076afbf8acde362f136dece42ef4d
- simulation status: COMPLETE
- alpha_id: 6Xa8lej5
- sharpe: 0.99
- fitness: 0.74
- turnover: 0.0923
- margin: 0.001514
- drawdown: 0.0987
- returns: 0.0699
- grade: INFERIOR
- platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, SELF_CORRELATION=PENDING
- hopeful: yes
- internal candidate: no
- comparison against V2: materially lower Sharpe and fitness, lower turnover, cleared LOW_SUB_UNIVERSE_SHARPE
- decision: over-smoothed; not a lead

### corr120_decay10_subindustry

```text
group_neutralize(ts_decay_linear(rank(ts_delta(close, 10)) * -rank(ts_corr(rank(close), rank(volume), 120)), 10), subindustry)
```

- fingerprint: dad311d46b426baa1efbd83ff3e7182b
- simulation status: COMPLETE
- alpha_id: mLr3j5Wp
- sharpe: 0.95
- fitness: 0.69
- turnover: 0.1295
- margin: 0.001056
- drawdown: 0.0991
- returns: 0.0683
- grade: INFERIOR
- platform flags: LOW_SHARPE=FAIL, LOW_FITNESS=FAIL, LOW_SUB_UNIVERSE_SHARPE=FAIL, SELF_CORRELATION=PENDING
- hopeful: yes
- internal candidate: no
- comparison against V2: worse on Sharpe and fitness, still fails sub-universe
- decision: reject this extension direction

## Third-Round Decision

- new lead candidate: no
- LOW_SUB_UNIVERSE_SHARPE cleared: yes, for corr90_decay10_subindustry and corr90_decay20_subindustry
- LOW_FITNESS cleared: no
- improved both Sharpe and fitness vs V2: no
- current lead after third round: V2 / `kq17QGe8`
- submit now: no
- next step: keep V2 as lead, keep corr90 variants as robustness references, and do not submit until LOW_FITNESS and sub-universe behavior are both acceptable.
