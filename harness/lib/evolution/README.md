# BRAIN_LAB Evolution Sandbox

This package provides a fully offline expression evolution sandbox for BRAIN_LAB.

## Modules

- `engine.py` - `BrainEvolutionEngine`, the orchestration layer
- `models.py` - frozen dataclasses for `WinnerRecord` and `AlphaCandidate`
- `selection.py` - tournament selection helpers
- `crossover.py` - structure-aware crossover
- `mutation.py` - numeric, operator, field, and wrapper mutation helpers
- `population.py` - winner loading and generation artifact export

## Inputs

- Ledger source: `runs/evidence/result_ledger.db`
- Compiler validation: `harness/lib/compiler`
- Configuration: `harness/lib/evolution/evolution_config.json`

## Outputs

- Canonical generation JSON:
  `runs/evolution/generations/gen_###.json`
- Batch-view manifest:
  `runs/evolution/generations/gen_###.batch.json`
- Per-candidate expression files:
  `runs/evolution/generations/gen_###/expr/*.expr`
- Evolution log:
  `runs/evolution/evolution_log.jsonl`

## Quick Start

```python
from evolution import BrainEvolutionEngine

engine = BrainEvolutionEngine(
    db_path="runs/evidence/result_ledger.db",
    population_size=50,
    output_dir="runs/evolution/generations",
)
engine.load_winners()
engine.initialize_population()
engine.run(generations=2)
```

## Harness Bootstrap

To run the offline evolution sandbox through the existing harness wrapper and record a learning-loop artifact:

```bash
./harness/run-local-alpha-loop.sh \
  --evolution-bootstrap \
  --run-id evo-bootstrap-demo \
  --evolution-generations 3 \
  --evolution-min-winners 10
```

This records a summary under `runs/learning-loops/` and leaves the next batch input at
`runs/evolution/generations/gen_001.batch.json`.

You can also launch the same path from the session harness:

```bash
./harness/coding-session.sh evolution-bootstrap --run-id evo-bootstrap-demo
```

The sandbox is offline by default and does not write to the ledger or call WQB APIs.
