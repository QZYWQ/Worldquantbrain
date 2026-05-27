#!/usr/bin/env python3
"""
获取账户所有已提交的alpha详情
"""
import requests
import time
import json
import sys
sys.path.insert(0, '/Users/zpdedn/Documents/github/worldquantAPI/user')
from machine_lib import login

def get_all_submitted_alphas(s, max_results=500):
    """获取所有已提交的alpha（包括通过和失败的）"""
    alphas = []
    offset = 0
    page_size = 100

    while offset < max_results:
        url = f"https://api.worldquantbrain.com/users/self/alphas?limit={page_size}&offset={offset}&hidden=false&type!=SUPER"
        try:
            resp = s.get(url)
            if resp.status_code != 200:
                print(f"HTTP {resp.status_code}: {resp.content[:200]}")
                break

            data = resp.json()
            results = data.get('results', [])
            if not results:
                break

            for alpha in results:
                alphas.append(alpha)

            offset += page_size
            print(f"Fetched {len(alphas)} alphas...")

            if len(results) < page_size:
                break

        except Exception as e:
            print(f"Error at offset {offset}: {e}")
            break

    return alphas


def get_alpha_full_details(s, alpha_id):
    """获取单个alpha的完整详情"""
    try:
        resp = s.get(f"https://api.worldquantbrain.com/alphas/{alpha_id}")
        if resp.status_code != 200:
            return None
        return resp.json()
    except Exception as e:
        print(f"Error fetching {alpha_id}: {e}")
        return None


def main():
    s = login()

    print("Fetching all submitted alphas...")
    alphas = get_all_submitted_alphas(s, max_results=500)
    print(f"\nTotal alphas retrieved: {len(alphas)}")

    # 按状态分组
    submitted = []
    for alpha in alphas:
        status = alpha.get('status', 'UNKNOWN')
        is_data = alpha.get('is', {})
        sharpe = is_data.get('sharpe', 0)
        fitness = is_data.get('fitness', 0)

        if status == 'SUBMITTED':
            submitted.append(alpha)

    print(f"Submitted (accepted): {len(submitted)}")

    # 获取详细信息的alpha ID列表
    print("\nFetching full details for submitted alphas...")
    detailed_alphas = []

    for i, alpha in enumerate(submitted):
        alpha_id = alpha.get('id')
        print(f"[{i+1}/{len(submitted)}] {alpha_id}")

        details = get_alpha_full_details(s, alpha_id)
        if details:
            detailed_alphas.append(details)

        time.sleep(0.5)

    # 保存完整结果
    output_file = "/Users/zpdedn/Documents/project/Worldquantbrain/runs/research-queues/2026-05-22-account-submitted-alphas-full.json"
    with open(output_file, 'w') as f:
        json.dump(detailed_alphas, f, indent=2)

    print(f"\nSaved to: {output_file}")

    # 生成摘要表格
    print("\n" + "="*120)
    print("SUBMITTED ALPHAS SUMMARY")
    print("="*120)
    print(f"{'Alpha ID':<15} {'Sharpe':>8} {'Fitness':>8} {'TVR':>8} {'SubU':>8} {'SC':>8} {'Decay':>6} {'Neutralization':<15} {'Expression':<60}")
    print("-"*120)

    for alpha in detailed_alphas:
        alpha_id = alpha.get('id', '')
        is_data = alpha.get('is', {})
        settings = alpha.get('settings', {})

        sharpe = is_data.get('sharpe', 0)
        fitness = is_data.get('fitness', 0)
        turnover = is_data.get('turnover', 0)
        margin = is_data.get('margin', 0)
        long_count = is_data.get('longCount', 0)
        short_count = is_data.get('shortCount', 0)

        # 从checks获取SubU和SC
        subu_value = "N/A"
        sc_value = "N/A"
        checks = is_data.get('checks', [])
        for check in checks:
            if check.get('name') == 'LOW_SUB_UNIVERSE_SHARPE':
                subu_value = f"{check.get('value', 0):.2f}"
            if check.get('name') == 'SELF_CORRELATION':
                sc_value = f"{check.get('value', 0):.4f}"

        decay = settings.get('decay', 0)
        neutralization = settings.get('neutralization', '')

        regular = alpha.get('regular', {})
        expression = regular.get('code', '')[:60] if regular else ''

        print(f"{alpha_id:<15} {sharpe:>8.2f} {fitness:>8.2f} {turnover:>8.4f} {subu_value:>8} {sc_value:>8} {decay:>6} {neutralization:<15} {expression:<60}")

    # 统计信息
    sharpes = [a.get('is', {}).get('sharpe', 0) for a in detailed_alphas]
    fitnesses = [a.get('is', {}).get('fitness', 0) for a in detailed_alphas]

    print("\n" + "="*60)
    print("STATISTICS")
    print("="*60)
    print(f"Count: {len(detailed_alphas)}")
    print(f"Sharpe - Min: {min(sharpes):.2f}, Max: {max(sharpes):.2f}, Avg: {sum(sharpes)/len(sharpes):.2f}")
    print(f"Fitness - Min: {min(fitnesses):.2f}, Max: {max(fitnesses):.2f}, Avg: {sum(fitnesses)/len(fitnesses):.2f}")

    return detailed_alphas


if __name__ == "__main__":
    main()