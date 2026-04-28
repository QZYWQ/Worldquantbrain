#!/usr/bin/env bash
set -euo pipefail

# Fixed local repo roots for the lightweight miner-to-brain workflow.
MINER_ROOT="/Users/zpdedn/Documents/github/worldquant-miner"
BRAIN_ROOT="/Users/zpdedn/Documents/project/Worldquantbrain"

# Run exactly one miner batch from the production repo. PYTHONPYCACHEPREFIX keeps
# transient bytecode outside the miner checkout.
cd "$MINER_ROOT"
PYTHONPYCACHEPREFIX=/tmp/worldquant-miner-pycache \
  python3 generation_one/naive-ollama/alpha_generator_ollama.py \
    --batch-size 1 \
    --max-batches 1

# Import the latest miner output back into the research repo without modifying
# the miner checkout.
cd "$BRAIN_ROOT"
python3 tools/import_miner_batch.py \
  --miner-root "$MINER_ROOT" \
  --brain-root "$BRAIN_ROOT"
