#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(cd -- "${HARNESS_ROOT}/.." && pwd)"

cd "$PROJECT_ROOT"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

valid_json="${tmpdir}/valid-candidate-batch.json"
invalid_json="${tmpdir}/invalid-candidate-batch.json"
valid_readiness_json="${tmpdir}/valid-field-readiness.json"
invalid_readiness_json="${tmpdir}/invalid-field-readiness.json"
valid_capability_json="${tmpdir}/valid-account-capability.json"
invalid_capability_json="${tmpdir}/invalid-account-capability.json"
valid_contract_json="${tmpdir}/valid-research-contract.json"
invalid_contract_json="${tmpdir}/invalid-research-contract.json"
valid_evidence_json="${tmpdir}/valid-evidence-ladder.json"
invalid_evidence_json="${tmpdir}/invalid-evidence-ladder.json"
valid_signflip_json="${tmpdir}/valid-signflip-capture.json"
invalid_signflip_json="${tmpdir}/invalid-signflip-capture.json"
valid_late_signflip_json="${tmpdir}/valid-late-signflip-capture.json"
invalid_late_signflip_json="${tmpdir}/invalid-late-signflip-capture.json"

cat >"$valid_json" <<'EOF'
{
  "candidates": [
    {
      "name": "baseline",
      "delay": 1,
      "sharpe": 1.64,
      "fitness": 1.03,
      "turnover": 0.1732,
      "max_weight": null,
      "max_weight_check": "PASS",
      "self_corr": null,
      "self_corr_check": "PASS",
      "subuniverse_pass": true,
      "test_period_pass": null,
      "test_period_observation": "Official alpha check did not emit a boolean; test slice stayed positive but weak.",
      "notes": "Official check endpoints resolved concentration and self-correlation, but not a numeric max weight."
    }
  ]
}
EOF

cat >"$invalid_json" <<'EOF'
{
  "candidates": [
    {
      "name": "missing-fallback",
      "delay": 1,
      "sharpe": 1.64,
      "fitness": 1.03,
      "turnover": 0.1732,
      "max_weight": null,
      "self_corr": null,
      "subuniverse_pass": true,
      "test_period_pass": null,
      "notes": "This batch forgot to explain unavailable optional fields."
    }
  ]
}
EOF

cat >"$valid_readiness_json" <<'EOF'
{
  "counts": {
    "family_count": 1,
    "pass_count": 1,
    "hold_count": 0,
    "block_count": 0
  },
  "items": [
    {
      "family_key": "good_family",
      "candidate_fields": ["good_signal"],
      "usable_candidate_fields": ["good_signal"],
      "blocked_candidate_fields": [],
      "coverage_by_field": {
        "good_signal": 100.0
      },
      "assessment": {
        "gate_status": "pass",
        "reasons": ["field-readiness gate passed"]
      }
    }
  ]
}
EOF

cat >"$invalid_readiness_json" <<'EOF'
{
  "counts": {
    "family_count": 1,
    "pass_count": 0,
    "hold_count": 1,
    "block_count": 0
  },
  "items": [
    {
      "family_key": "broken_family",
      "candidate_fields": ["broken_signal"],
      "usable_candidate_fields": [],
      "blocked_candidate_fields": [],
      "coverage_by_field": {},
      "assessment": {
        "gate_status": "stalled",
        "reasons": []
      }
    }
  ]
}
EOF

cat >"$valid_contract_json" <<'EOF'
{
  "counts": {
    "family_count": 1,
    "pass_count": 1,
    "hold_count": 0,
    "block_count": 0
  },
  "items": [
    {
      "family_key": "good_family",
      "source_family_doc_paths": ["runs/expression-families/good-family.md"],
      "contract": {
        "mechanism": "slow_ratio",
        "universe": "TOP3000"
      },
      "assessment": {
        "gate_status": "pass",
        "reasons": ["research-contract gate passed"]
      }
    }
  ]
}
EOF

cat >"$valid_capability_json" <<'EOF'
{
  "counts": {
    "family_count": 1,
    "pass_count": 1,
    "hold_count": 0,
    "block_count": 0
  },
  "items": [
    {
      "family_key": "good_family",
      "required_scope": {
        "region": "USA",
        "delay": "1",
        "universe": "TOP3000",
        "data_category": "fundamental"
      },
      "capability_snapshot": {
        "observed_combo_count": 1,
        "observed_regions": ["USA"],
        "observed_delays": ["1"],
        "observed_universes": ["TOP3000"],
        "observed_categories": ["fundamental"],
        "required_combo": "USA|1|TOP3000",
        "matching_combo": {
          "region": "USA",
          "delay": "1",
          "universe": "TOP3000",
          "field_count": 10,
          "category_counts": {
            "fundamental": 10
          },
          "dataset_counts": {
            "fundamental": 10
          },
          "samples": []
        },
        "public_tier_notes": []
      },
      "assessment": {
        "gate_status": "pass",
        "reasons": ["required scope is represented in the local capability snapshot"]
      }
    }
  ]
}
EOF

cat >"$invalid_capability_json" <<'EOF'
{
  "counts": {
    "family_count": 1,
    "pass_count": 0,
    "hold_count": 0,
    "block_count": 1
  },
  "items": [
    {
      "family_key": "broken_family",
      "required_scope": {
        "region": "USA"
      },
      "capability_snapshot": {
        "observed_combo_count": -1,
        "observed_regions": "USA",
        "observed_delays": [],
        "observed_universes": [],
        "observed_categories": [],
        "required_combo": null,
        "matching_combo": [],
        "public_tier_notes": []
      },
      "assessment": {
        "gate_status": "unknown",
        "reasons": []
      }
    }
  ]
}
EOF

cat >"$invalid_contract_json" <<'EOF'
{
  "counts": {
    "family_count": 1,
    "pass_count": 0,
    "hold_count": 1,
    "block_count": 0
  },
  "items": [
    {
      "family_key": "broken_family",
      "source_family_doc_paths": [],
      "contract": {},
      "assessment": {
        "gate_status": "unknown",
        "reasons": []
      }
    }
  ]
}
EOF

cat >"$valid_evidence_json" <<'EOF'
{
  "counts": {
    "family_count": 1,
    "E0_front_gate_only": 1,
    "E1_local_support": 0,
    "E2_partial_official": 0,
    "E3_full_is": 0,
    "E4_submit_ready": 0
  },
  "items": [
    {
      "family_key": "good_family",
      "counts": {
        "official_outcome_count": 0
      },
      "assessment": {
        "evidence_level": "E0_front_gate_only",
        "evidence_source": "front_gate_only",
        "promotion_ceiling": "explore",
        "effective_state": "explore",
        "branch_budget_remaining": 0,
        "official_budget_cap": 1,
        "reasons": ["front gates only"]
      }
    }
  ]
}
EOF

cat >"$invalid_evidence_json" <<'EOF'
{
  "counts": {
    "family_count": 1,
    "E0_front_gate_only": 0,
    "E1_local_support": 1,
    "E2_partial_official": 0,
    "E3_full_is": 0,
    "E4_submit_ready": 0
  },
  "items": [
    {
      "family_key": "broken_family",
      "counts": {},
      "assessment": {
        "evidence_level": "bad_level",
        "evidence_source": "",
        "promotion_ceiling": "bad_ceiling",
        "effective_state": "bad_state",
        "branch_budget_remaining": -1,
        "official_budget_cap": 0,
        "reasons": []
      }
    }
  ]
}
EOF

cat >"$valid_signflip_json" <<'EOF'
{
  "capture_id": "valid-signflip-policy-01",
  "topic": "signflip-policy",
  "batch_policy": {
    "required_sign_flip_source_index": 0,
    "required_sign_flip_reason": "Baseline Sharpe is negative, so the very next control must flip the final executable expression."
  },
  "alphas": [
    {
      "name": "baseline",
      "expression": "scl12_sentiment_fast_d1",
      "metrics": {
        "sharpe": -0.51,
        "fitness": -0.13,
        "turnover": 0.7602,
        "returns": -0.0512,
        "max_weight": null
      },
      "tests": {
        "subuniverse_pass": false,
        "test_period_pass": null,
        "check_submission_pass": null
      },
      "notes": "Mandatory sign flip required after the negative baseline."
    },
    {
      "name": "sign_flip",
      "expression": "-scl12_sentiment_fast_d1",
      "metrics": {
        "sharpe": 0.51,
        "fitness": 0.13,
        "turnover": 0.7602,
        "returns": 0.0512,
        "max_weight": null
      },
      "tests": {
        "subuniverse_pass": true,
        "test_period_pass": null,
        "check_submission_pass": null
      },
      "notes": "Immediate sign-flipped control."
    }
  ]
}
EOF

cat >"$invalid_signflip_json" <<'EOF'
{
  "capture_id": "invalid-signflip-policy-01",
  "topic": "signflip-policy",
  "batch_policy": {
    "required_sign_flip_source_index": 0,
    "required_sign_flip_reason": "Baseline Sharpe is negative, so the next control must flip the final executable expression."
  },
  "alphas": [
    {
      "name": "baseline",
      "expression": "scl12_sentiment_fast_d1",
      "metrics": {
        "sharpe": -0.51,
        "fitness": -0.13,
        "turnover": 0.7602,
        "returns": -0.0512,
        "max_weight": null
      },
      "tests": {
        "subuniverse_pass": false,
        "test_period_pass": null,
        "check_submission_pass": null
      },
      "notes": "Mandatory sign flip required after the negative baseline."
    },
    {
      "name": "wrong_control",
      "expression": "ts_rank(scl12_sentiment_fast_d1, 20)",
      "metrics": {
        "sharpe": 0.21,
        "fitness": 0.05,
        "turnover": 0.2311,
        "returns": 0.0132,
        "max_weight": null
      },
      "tests": {
        "subuniverse_pass": true,
        "test_period_pass": null,
        "check_submission_pass": null
      },
      "notes": "This is not the required sign-flip control."
    }
  ]
}
EOF

cat >"$valid_late_signflip_json" <<'EOF'
{
  "capture_id": "valid-late-signflip-policy-01",
  "topic": "signflip-policy",
  "batch_policy": {
    "required_sign_flip_source_index": 1,
    "required_sign_flip_reason": "The first simple control is negative, so the next control must flip that exact expression."
  },
  "alphas": [
    {
      "name": "baseline",
      "expression": "group_rank(ts_rank(scl12_sentiment_fast_d1, 60), industry)",
      "metrics": {
        "sharpe": 0.42,
        "fitness": 0.11,
        "turnover": 0.241,
        "returns": 0.0184,
        "max_weight": null
      },
      "tests": {
        "subuniverse_pass": true,
        "test_period_pass": null,
        "check_submission_pass": null
      },
      "notes": "The baseline is positive; the next control is the first negative simple control."
    },
    {
      "name": "first_control",
      "expression": "group_rank(ts_rank(scl12_sentiment_fast_d1, 20), industry)",
      "metrics": {
        "sharpe": -0.31,
        "fitness": -0.08,
        "turnover": 0.231,
        "returns": -0.0132,
        "max_weight": null
      },
      "tests": {
        "subuniverse_pass": false,
        "test_period_pass": null,
        "check_submission_pass": null
      },
      "notes": "This negative control requires an immediate sign flip."
    },
    {
      "name": "late_sign_flip",
      "expression": "-group_rank(ts_rank(scl12_sentiment_fast_d1, 20), industry)",
      "metrics": {
        "sharpe": 0.31,
        "fitness": 0.08,
        "turnover": 0.231,
        "returns": 0.0132,
        "max_weight": null
      },
      "tests": {
        "subuniverse_pass": true,
        "test_period_pass": null,
        "check_submission_pass": null
      },
      "notes": "Immediate sign-flipped follow-up."
    }
  ]
}
EOF

cat >"$invalid_late_signflip_json" <<'EOF'
{
  "capture_id": "invalid-late-signflip-policy-01",
  "topic": "signflip-policy",
  "batch_policy": {
    "required_sign_flip_source_index": 1,
    "required_sign_flip_reason": "The first simple control is negative, so the next control must flip that exact expression."
  },
  "alphas": [
    {
      "name": "baseline",
      "expression": "group_rank(ts_rank(scl12_sentiment_fast_d1, 60), industry)",
      "metrics": {
        "sharpe": 0.42,
        "fitness": 0.11,
        "turnover": 0.241,
        "returns": 0.0184,
        "max_weight": null
      },
      "tests": {
        "subuniverse_pass": true,
        "test_period_pass": null,
        "check_submission_pass": null
      },
      "notes": "The baseline is positive; the next control is the first negative simple control."
    },
    {
      "name": "first_control",
      "expression": "group_rank(ts_rank(scl12_sentiment_fast_d1, 20), industry)",
      "metrics": {
        "sharpe": -0.31,
        "fitness": -0.08,
        "turnover": 0.231,
        "returns": -0.0132,
        "max_weight": null
      },
      "tests": {
        "subuniverse_pass": false,
        "test_period_pass": null,
        "check_submission_pass": null
      },
      "notes": "This negative control requires an immediate sign flip."
    },
    {
      "name": "wrong_follow_up",
      "expression": "ts_rank(scl12_sentiment_fast_d1, 10)",
      "metrics": {
        "sharpe": 0.09,
        "fitness": 0.02,
        "turnover": 0.156,
        "returns": 0.0031,
        "max_weight": null
      },
      "tests": {
        "subuniverse_pass": true,
        "test_period_pass": null,
        "check_submission_pass": null
      },
      "notes": "This is not the required sign-flipped follow-up."
    }
  ]
}
EOF

python3 harness/lib/content-validator.py --mode candidate-batch-json --path "$valid_json"
python3 harness/lib/content-validator.py --mode field-readiness-json --path "$valid_readiness_json"
python3 harness/lib/content-validator.py --mode account-capability-json --path "$valid_capability_json"
python3 harness/lib/content-validator.py --mode research-contract-json --path "$valid_contract_json"
python3 harness/lib/content-validator.py --mode evidence-ladder-json --path "$valid_evidence_json"
python3 harness/lib/content-validator.py --mode manual-artifact --path "$valid_signflip_json"
python3 harness/lib/content-validator.py --mode manual-artifact --path "$valid_late_signflip_json"

if python3 harness/lib/content-validator.py --mode candidate-batch-json --path "$invalid_json"; then
  echo "content-validator should reject candidate batches that omit fallback explanations" >&2
  exit 1
fi

if python3 harness/lib/content-validator.py --mode field-readiness-json --path "$invalid_readiness_json"; then
  echo "content-validator should reject invalid field-readiness payloads" >&2
  exit 1
fi

if python3 harness/lib/content-validator.py --mode account-capability-json --path "$invalid_capability_json"; then
  echo "content-validator should reject invalid account-capability payloads" >&2
  exit 1
fi

if python3 harness/lib/content-validator.py --mode research-contract-json --path "$invalid_contract_json"; then
  echo "content-validator should reject invalid research-contract payloads" >&2
  exit 1
fi

if python3 harness/lib/content-validator.py --mode evidence-ladder-json --path "$invalid_evidence_json"; then
  echo "content-validator should reject invalid evidence-ladder payloads" >&2
  exit 1
fi

if python3 harness/lib/content-validator.py --mode manual-artifact --path "$invalid_signflip_json"; then
  echo "content-validator should reject simulation captures that skip the required sign-flip control" >&2
  exit 1
fi

if python3 harness/lib/content-validator.py --mode manual-artifact --path "$invalid_late_signflip_json"; then
  echo "content-validator should reject simulation captures that skip the required sign-flip control after a negative first simple control" >&2
  exit 1
fi

printf 'Harness content validator test passed.\n'
