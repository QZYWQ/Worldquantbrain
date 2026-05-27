#!/usr/bin/env python3
"""
批量模拟Alpha变体 - 提交到新账户
"""
import requests
import time
import json
import sys
from pathlib import Path
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import login

API_BASE = 'https://api.worldquantbrain.com'
VARIATIONS_FILE = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-22-alpha-variations.json')
OUTPUT_FILE = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-22-alpha-variations-results.json')

# 加载变体
with VARIATIONS_FILE.open('r') as f:
    variations = json.load(f)

print(f"加载了 {len(variations)} 个Alpha变体")

# 基础设置
BASE_SETTINGS = {
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,
    "truncation": 0.08,
    "pasteurization": "ON",
    "unitHandling": "VERIFY",
    "nanHandling": "OFF",
    "maxTrade": "OFF",
    "maxPosition": "OFF",
    "language": "FASTEXPR",
    "visualization": False,
    "startDate": "2019-01-01",
    "endDate": "2023-12-31",
}

def load_existing_results():
    if not OUTPUT_FILE.exists():
        return {}
    with OUTPUT_FILE.open('r') as f:
        existing = json.load(f)
    return {
        item["original_id"]: item
        for item in existing
        if isinstance(item, dict) and item.get("original_id")
    }


def save_results(result_map):
    ordered = [
        result_map[var["id"]]
        for var in variations
        if var["id"] in result_map
    ]
    tmp_file = OUTPUT_FILE.with_suffix(".json.tmp")
    with tmp_file.open('w') as f:
        json.dump(ordered, f, indent=2)
    tmp_file.replace(OUTPUT_FILE)


def parse_retry_after(response, default=10):
    try:
        return float(response.headers.get('Retry-After', default))
    except (TypeError, ValueError):
        return default


def fetch_alpha_details(s, alpha_id):
    try:
        response = s.get(f'{API_BASE}/alphas/{alpha_id}', timeout=60)
        if response.status_code != 200:
            return {
                "fetch_status": response.status_code,
                "fetch_error": response.text[:500],
            }
        return response.json()
    except Exception as e:
        return {"fetch_error": str(e)}


def metric_summary(alpha_details):
    if not isinstance(alpha_details, dict):
        return {}
    is_metrics = alpha_details.get("is") or {}
    keys = [
        "sharpe",
        "fitness",
        "turnover",
        "returns",
        "drawdown",
        "margin",
        "longCount",
        "shortCount",
        "weight",
        "subUniverseSharpe",
    ]
    return {key: is_metrics.get(key) for key in keys if key in is_metrics}


def simulate_alpha(s, expression, settings, alpha_id):
    """提交模拟并等待结果"""
    full_settings = dict(BASE_SETTINGS)
    full_settings.update(settings)

    payload = {
        "type": "REGULAR",
        "settings": full_settings,
        "regular": expression,
    }

    try:
        r = None
        for attempt in range(1, 6):
            r = s.post(f'{API_BASE}/simulations', json=payload, timeout=60)
            if r.status_code in (429, 500, 502, 503, 504):
                wait_seconds = parse_retry_after(r, default=min(60, 5 * attempt))
                print(f"  HTTP {r.status_code}; retrying in {wait_seconds:.1f}s")
                time.sleep(wait_seconds)
                continue
            break

        if r.status_code != 201:
            print(f"  HTTP {r.status_code}: {r.content[:200]}")
            return {"status": "FAILED", "http_status": r.status_code, "error": r.text[:500]}

        url = r.headers.get('Location')
        if not url:
            return {"status": "FAILED", "error": "Missing simulation Location header"}

        # 轮询
        for _ in range(120):
            prog = s.get(url, timeout=60)
            h = prog.headers

            if h.get('Retry-After'):
                time.sleep(float(h['Retry-After']))
                continue

            result = prog.json()
            status = result.get('status')

            if status in ('COMPLETE', 'WARNING') and result.get('alpha'):
                alpha_id_result = result.get('alpha')
                alpha_details = fetch_alpha_details(s, alpha_id_result)
                return {
                    "status": "SUCCESS",
                    "new_alpha_id": alpha_id_result,
                    "simulation_status": status,
                    "metrics": metric_summary(alpha_details),
                    "alpha_details": alpha_details,
                }

            if status == 'FAILED':
                print(f"  Simulation failed")
                return {"status": "FAILED", "simulation_status": status, "simulation_result": result}

            time.sleep(1)

        return {"status": "FAILED", "error": "Timed out waiting for simulation result"}

    except Exception as e:
        print(f"  Error: {e}")
        return {"status": "FAILED", "error": str(e)}


def run_batch():
    s = login()
    result_map = load_existing_results()

    print(f"\n开始批量模拟 {len(variations)} 个Alpha变体...")
    if result_map:
        success_count = sum(1 for r in result_map.values() if r.get('status') == 'SUCCESS')
        print(f"已加载历史结果: {len(result_map)} 条，其中成功 {success_count} 条")
    print("="*80)

    for i, var in enumerate(variations):
        alpha_id = var['id']
        expression = var['regular']['code']
        settings = var['settings']

        if result_map.get(alpha_id, {}).get('status') == 'SUCCESS':
            print(f"\n[{i+1}/{len(variations)}] {alpha_id} already SUCCESS, skipping")
            continue

        print(f"\n[{i+1}/{len(variations)}] {alpha_id}")
        print(f"  Expression: {expression[:80]}...")
        print(f"  Settings: decay={settings.get('decay', 0)}, neutral={settings.get('neutralization', 'N/A')}")

        result = simulate_alpha(s, expression, settings, alpha_id)

        if result.get("status") == "SUCCESS":
            print(f"  ✅ Success: {result['new_alpha_id']}")
            result_map[alpha_id] = {
                "original_id": alpha_id,
                "expression": expression,
                "settings": settings,
                **result,
            }
        else:
            print(f"  ❌ Failed")
            result_map[alpha_id] = {
                "original_id": alpha_id,
                "expression": expression,
                "settings": settings,
                **result,
            }

        save_results(result_map)

        # 3秒间隔避免rate limit
        time.sleep(3)

        # 每20个报告进度
        if (i + 1) % 20 == 0:
            success_count = sum(1 for r in result_map.values() if r.get('status') == 'SUCCESS')
            print(f"\n--- 进度报告: {i+1}/{len(variations)}, 成功: {success_count} ---")

    # 保存结果
    save_results(result_map)

    print(f"\n完成! 结果保存到: {OUTPUT_FILE}")

    # 统计
    results = [
        result_map[var["id"]]
        for var in variations
        if var["id"] in result_map
    ]
    success = [r for r in results if r.get('status') == 'SUCCESS']
    failed = [r for r in results if r.get('status') == 'FAILED']
    print(f"\n成功: {len(success)}, 失败: {len(failed)}")

    return results


if __name__ == "__main__":
    run_batch()
