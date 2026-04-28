# Runbook

## 1. Static checks

Worldquantbrain:
```bash
python3 -m py_compile tools/import_miner_batch.py
bash -n tools/run_miner_once.sh
python3 -m py_compile tools/task_runner.py
```

miner:
```bash
PYTHONPYCACHEPREFIX=/tmp/worldquant-miner-pycache python3 -m py_compile generation_one/naive-ollama/alpha_generator_ollama.py
python3 -m unittest tests/test_feedback_generator.py
git diff --check
```

## 2. One-shot feedback-aware validation

```bash
cd /Users/zpdedn/Documents/project/Worldquantbrain
tools/run_miner_once.sh
```

## 3. Task queue

```bash
cd /Users/zpdedn/Documents/project/Worldquantbrain
python3 tools/task_runner.py init
python3 tools/task_runner.py list
python3 tools/task_runner.py claim-next
python3 tools/task_runner.py heartbeat --task-id <id>
python3 tools/task_runner.py complete --task-id <id> --summary "..."
python3 tools/task_runner.py fail --task-id <id> --reason "..."
```

## 4. Git hygiene

- Worldquantbrain can commit tools/, docs/, runs/notes/, selected runs archives.
- miner can commit source and tests.
- Do not commit credential.txt.
- Do not blindly commit ledger.csv, fingerprints.json, hopeful_alphas.json, results/.
