#!/usr/bin/env python3
"""
Alpha 升阶Master Pipeline
================================
Step 1: 获取所有UNSUBMITTED alpha + 已提交记录
Step 2: 识别7-pass需要升阶的候选
Step 3: 执行SO/TH升阶策略
Step 4: 评分排序 (经济逻辑 > 非继承 > 低自相关 > Sharpe > Fitness > Turnover)
Step 5: 标记Favorite
Step 6: 生成最终汇总报告

Usage:
    python3 alpha_master_upgrade.py [--mode full|rank-only|favorite-only] [--pass-sharpe 1.5]
"""

import sys, json, time, os
from pathlib import Path
from datetime import datetime
import requests

# ============================================================
# CONFIG
# ============================================================
OUTPUT_DIR = Path('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load credentials from credential.txt
_cred_path = Path('/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt')
try:
    _cred_data = json.loads(_cred_path.read_text().strip())
    if isinstance(_cred_data, list) and len(_cred_data) >= 2:
        CREDENTIALS = (_cred_data[0], _cred_data[1])
    elif isinstance(_cred_data, dict):
        CREDENTIALS = (_cred_data.get('username', _cred_data.get('user', _cred_data.get('email'))),
                       _cred_data.get('password', ''))
    else:
        raise ValueError("Unexpected credential format")
except Exception as e:
    print(f'Failed to load credentials: {e}', flush=True)
    sys.exit(1)
print(f'Using account: {CREDENTIALS[0]}', flush=True)

# 已提交的alpha ID (旧账户已提交的，新账户用来规避family冲突)
AVOID_FAMILIES = [
    'O0bXoVV1', 'LLgOWZmn', '88Ob79jV', 'GrnExm2Q', 'e7dPWeop',
    'A1gVE97w', 'bloqmdJK', 'A1g6AlWg', 'Xg2X2jxl', 'E5g7vMjJ',
    'E5repQ81', 'd5l07rpX', 'gJmojOQm', '0mAE3qzp', '1YodbWO6',
    '2rvNV1qJ', 'RRNmMErj', '1YopVrdW', 'xAeN6jGp', '1YoX2GxX',
    'QPn0vn3X'
]

# 经济逻辑优先级分级
ECONOMIC_PRIORITY = {
    'earnings': 1, 'eps': 1, 'revenue': 1, 'sales': 1, 'fnd6': 1,
    'anl4': 1, 'profit': 1, 'income': 1, 'ebit': 1, 'cashflow': 1,
    'dividend': 1, 'book_value': 1, 'equity': 1, 'assets': 1,
    'liabilities': 1, 'debt': 1, 'margin': 1, 'roa': 1, 'roe': 1,
    'tobins_q': 1, 'fn_comp': 1, 'fn_interest': 1,
    'close': 2, 'open': 2, 'high': 2, 'low': 2, 'vwap': 2,
    'volume': 2, 'returns': 2, 'price': 2, 'cap': 2,
    'scl12': 3, 'sentiment': 3, 'buzz': 3, 'news': 3,
    'model': 4, 'mdl': 4, 'multi_factor': 4, 'growth_potential': 4,
    'unsystematic': 4, 'hvol': 4, 'pcr': 4, 'vsm': 4,
}

# Thresholds
PASS_SHARPE = 1.5
PASS_FITNESS = 1.0
MAX_TURNOVER = 0.6
MAX_SELFCORR = 0.7

# ============================================================
# API Functions
# ============================================================

def login():
    sess = requests.Session()
    sess.auth = CREDENTIALS
    r = sess.post('https://api.worldquantbrain.com/authentication')
    status = r.status_code
    print(f'[AUTH] {status}', flush=True)
    if status != 201:
        print(f'  Response: {r.text[:200]}', flush=True)
    return sess

def get_alpha_detail(sess, alpha_id):
    """获取alpha详细信息"""
    r = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}')
    if r.status_code != 200:
        return None
    return r.json()

def get_expression(ad):
    """从alpha detail提取expression"""
    reg = ad.get('regular', {})
    if isinstance(reg, dict):
        return reg.get('code', '')
    return str(reg)

def get_alpha_checks(sess, alpha_id):
    """获取alpha check详情"""
    r = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}/check')
    if r.status_code != 200:
        return None, None

    data = r.json()
    is_data = data.get('is', {})
    checks = is_data.get('checks', [])

    check_map = {}
    for c in checks:
        check_map[c['name']] = {
            'result': c.get('result'),
            'value': c.get('value')
        }

    selfcorr = None
    for c in checks:
        if c['name'] == 'SELF_CORRELATION':
            selfcorr = c.get('value')
            break

    return check_map, selfcorr

def check_alpha_submission(sess, alpha_id, gold_bag_ids, start=0, max_check=50):
    """批量检查alpha提交资格"""
    result = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}/check')
    if result.status_code != 200:
        return None, 'API_ERROR'

    # Handle retry
    data = result.json()
    is_data = data.get('is', {})
    checks = is_data.get('checks', [])

    selfcorr = None
    all_pass = True
    fail_reason = None
    for c in checks:
        if c['name'] == 'SELF_CORRELATION':
            selfcorr = c.get('value')
        if c.get('result') != 'PASS':
            all_pass = False
            fail_reason = c.get('name', 'UNKNOWN')

    return selfcorr, 'PASS' if all_pass else f'FAIL_{fail_reason}'

def simulate_upgrade(sess, expr, name, decay=0, neutralization='SUBINDUSTRY'):
    """模拟单个alpha升级变体"""
    settings = {
        'instrumentType': 'EQUITY', 'region': 'USA', 'universe': 'TOP3000',
        'delay': 1, 'decay': decay, 'neutralization': neutralization,
        'truncation': 0.08, 'pasteurization': 'ON',
        'testPeriod': 'P2Y', 'unitHandling': 'VERIFY', 'nanHandling': 'ON',
        'language': 'FASTEXPR', 'visualization': False,
    }
    r = sess.post('https://api.worldquantbrain.com/simulations',
                  json={'type': 'REGULAR', 'settings': settings, 'regular': expr})
    if r.status_code != 201:
        return None
    url = r.headers['Location']
    for _ in range(120):
        prog = sess.get(url)
        h = prog.headers
        if h.get('Retry-After'):
            time.sleep(float(h['Retry-After']))
            continue
        result = prog.json()
        status = result.get('status')
        alpha_id = result.get('alpha')
        if status in ('COMPLETE', 'WARNING') and alpha_id:
            ad = sess.get(f'https://api.worldquantbrain.com/alphas/{alpha_id}').json()
            is_m = ad.get('is', {})
            return {
                'alpha_id': alpha_id, 'name': name, 'expression': expr,
                'sharpe': is_m.get('sharpe'), 'fitness': is_m.get('fitness'),
                'turnover': is_m.get('turnover'), 'margin': is_m.get('margin'),
                'longCount': is_m.get('longCount', 0), 'shortCount': is_m.get('shortCount', 0),
                'decay': decay, 'neutralization': neutralization
            }
        elif status == 'ERROR':
            return None
        time.sleep(5)
    return None

def mark_favorite(sess, alpha_id, favorite=True):
    """标记alpha为favorite"""
    r = sess.patch(f'https://api.worldquantbrain.com/alphas/{alpha_id}', json={
        'color': 'YELLOW' if favorite else None,
        'tags': ['favorite'] if favorite else []
    })
    return r.status_code in (200, 204)

# ============================================================
# Scoring Functions
# ============================================================

def score_economic_priority(expr):
    """根据表达式中的field判断经济逻辑优先级 (1=最高, 5=最低)"""
    expr_lower = expr.lower()

    best_priority = 5
    for keyword, priority in ECONOMIC_PRIORITY.items():
        if keyword in expr_lower:
            best_priority = min(best_priority, priority)

    return best_priority

def score_inheritance(expr, submitted_exprs):
    """检测是否继承自已提交alpha"""
    expr_simple = expr.replace(' ', '')

    for sub_expr in submitted_exprs:
        sub_simple = sub_expr.replace(' ', '')
        # 检查是否是变体 (共享核心部分)
        common_core = find_common_core(expr_simple, sub_simple)
        if common_core and len(common_core) > 30:
            return 2  # 高度继承

    return 1  # 独立alpha

def find_common_core(e1, e2):
    """找两个表达式的最长公共子串"""
    if len(e1) > len(e2):
        e1, e2 = e2, e1

    longest = ''
    for i in range(len(e1)):
        for j in range(i + len(longest) + 1, len(e1) + 1):
            if e1[i:j] in e2:
                longest = e1[i:j]

    return longest if len(longest) > 5 else ''

def extract_base_field(expr):
    """从表达式中提取基础field"""
    fields_found = []
    for keyword in ['fnd6_', 'anl4_', 'mdl', 'scl12_', 'tobins_', 'earnings_', 'revenue_',
                    'sales_', 'fn_comp', 'fn_interest', 'unsystematic_', 'assets', 'cap',
                    'close', 'volume', 'returns', 'vwap', 'high', 'low',
                    'growth_potential', 'multi_factor']:
        if keyword in expr.lower():
            fields_found.append(keyword)
    return fields_found

def compute_total_score(alpha_info, submitted_exprs):
    """
    综合评分 (越低越好)
    权重:
    - 经济逻辑: 30%
    - 非继承: 20%
    - 低自相关: 20%
    - Sharpe: 15%
    - Fitness: 10%
    - Turnover: 5%
    """
    econ_score = score_economic_priority(alpha_info.get('expr', ''))
    inherit_score = score_inheritance(alpha_info.get('expr', ''), submitted_exprs)
    selfcorr = alpha_info.get('selfcorr', 1.0)
    sharpe = alpha_info.get('sharpe', 0)
    fitness = alpha_info.get('fitness', 0)
    turnover = alpha_info.get('turnover', 1.0)

    # Normalize to 0-1 scale
    norm_econ = (econ_score - 1) / 4  # 0=best econ, 1=worst econ
    norm_inherit = (inherit_score - 1) / 1  # 0=independent, 1=inherited
    norm_selfcorr = selfcorr / 0.7 if selfcorr else 0.5  # 0=no selfcorr, 1=at limit
    norm_sharpe = max(0, min(1, (1.5 - min(sharpe, 3.0)) / 1.5))  # higher sharpe = lower score
    norm_fitness = max(0, min(1, (1.0 - min(fitness, 2.0)) / 1.0))
    norm_turnover = max(0, min(1, turnover / 0.6))

    total = (
        norm_econ * 0.30 +
        norm_inherit * 0.20 +
        norm_selfcorr * 0.20 +
        norm_sharpe * 0.15 +
        norm_fitness * 0.10 +
        norm_turnover * 0.05
    )

    return total

# ============================================================
# Upgrade Strategies
# ============================================================

def build_upgrade_variants(base_expr, parent_id):
    """
    构建所有合理的升阶变体
    策略基于研究记忆中的关键发现:
    - rank() wrapper可降低自相关
    - decay窗口调整 (15是临界值)
    - group_neutralize分组变换
    """
    variants = []

    # === 策略1: rank包装 (已验证可降自相关) ===
    for decay in [0, 6]:
        variants.append({
            'name': f'{parent_id}_u1_rank_d{decay}',
            'expr': f'rank({base_expr})',
            'decay': decay, 'neut': 'SUBINDUSTRY',
            'strategy': 'rank_wrapper'
        })

    # === 策略2: rank + decay调整 ===
    for decay in [15]:
        variants.append({
            'name': f'{parent_id}_u2_rank_d{decay}',
            'expr': f'rank({base_expr})',
            'decay': decay, 'neut': 'SUBINDUSTRY',
            'strategy': 'rank_decay15'
        })

    # === 策略3: zscore包装 ===
    for decay in [0, 6]:
        variants.append({
            'name': f'{parent_id}_u3_zscore_d{decay}',
            'expr': f'zscore({base_expr})',
            'decay': decay, 'neut': 'SUBINDUSTRY',
            'strategy': 'zscore_wrapper'
        })

    # === 策略4: group_rank (market) ===
    variants.append({
        'name': f'{parent_id}_u4_grp_rank_mkt',
        'expr': f'group_rank({base_expr}, market)',
        'decay': 0, 'neut': 'SUBINDUSTRY',
        'strategy': 'group_rank_market'
    })

    # === 策略5: group_neutralize (切换group) ===
    for grp in ['sector', 'market']:
        variants.append({
            'name': f'{parent_id}_u5_neut_{grp}',
            'expr': f'group_neutralize({base_expr}, {grp})',
            'decay': 0, 'neut': grp.upper(),
            'strategy': f'neut_{grp}'
        })

    # === 策略6: densify(bucket(rank(cap))) wrapper (参考gJmojOQm成功) ===
    for decay in [0]:
        variants.append({
            'name': f'{parent_id}_u6_densify_cap_d{decay}',
            'expr': f'densify(bucket(rank(cap), range=\'0.1, 1, 0.1\'), {base_expr})',
            'decay': decay, 'neut': 'SUBINDUSTRY',
            'strategy': 'densify_cap_bucket'
        })

    # === 策略7: quantile减少极端值 ===
    for decay in [0, 6]:
        variants.append({
            'name': f'{parent_id}_u7_quantile_d{decay}',
            'expr': f'quantile({base_expr}, 0.1)',
            'decay': decay, 'neut': 'SUBINDUSTRY',
            'strategy': 'quantile_trim'
        })

    return variants

# ============================================================
# Main Pipeline
# ============================================================

def fetch_all_unsubmitted(sess, limit=200):
    """获取所有unsubmitted alpha"""
    all_alphas = []
    for offset in range(0, limit, 100):
        url = (f'https://api.worldquantbrain.com/users/self/alphas?limit=100&offset={offset}'
               f'&status=UNSUBMITTED&hidden=false&type!=SUPER')
        r = sess.get(url)
        if r.status_code != 200:
            break
        data = r.json()
        results = data.get('results', [])
        all_alphas.extend(results)
        if len(results) < 100:
            break
        time.sleep(1)

    return all_alphas

def fetch_submitted_exprs(sess):
    """获取已提交alpha的表达式"""
    exprs = []
    for aid in SUBMITTED_ALPHA_IDS:
        ad = get_alpha_detail(sess, aid)
        if ad:
            exprs.append(get_expression(ad))
        time.sleep(0.5)
    return exprs

def analyze_alpha(sess, alpha_data):
    """分析单个alpha的状态"""
    aid = alpha_data['id']
    is_data = alpha_data.get('is', {})
    sharpe = is_data.get('sharpe', 0)
    fitness = is_data.get('fitness', 0)
    turnover = is_data.get('turnover', 0)

    expr = ''
    reg = alpha_data.get('regular', {})
    if isinstance(reg, dict):
        expr = reg.get('code', '')

    decay = alpha_data.get('settings', {}).get('decay', 0)
    neut = alpha_data.get('settings', {}).get('neutralization', '')

    return {
        'alpha_id': aid,
        'expr': expr,
        'sharpe': sharpe,
        'fitness': fitness,
        'turnover': turnover,
        'decay': decay,
        'neutralization': neut,
        'fields': extract_base_field(expr)
    }

def step1_gather_candidates(sess):
    """Step 1: Gather all candidates"""
    print('\n' + '='*60, flush=True)
    print('STEP 1: 获取所有Alphas', flush=True)
    print('='*60, flush=True)

    unsubmitted = fetch_all_unsubmitted(sess)
    print(f'获取到 {len(unsubmitted)} 个unsubmitted alpha', flush=True)

    # 获取已提交表达式的
    submitted_exprs = fetch_submitted_exprs(sess)
    print(f'已获取 {len(submitted_exprs)} 个已提交alpha的表达式', flush=True)

    # 分析每个alpha
    candidates = []
    for a in unsubmitted:
        info = analyze_alpha(sess, a)
        candidates.append(info)

    # 获取check信息
    print('\n检查alpha状态...', flush=True)
    alpha_checks = {}
    for i, cand in enumerate(candidates):
        if i % 20 == 0 and i > 0:
            print(f'  已检查 {i}/{len(candidates)}', flush=True)

        aid = cand['alpha_id']
        # 只检查S>=1.0的
        if cand['sharpe'] < 1.0:
            continue

        checks, selfcorr = get_alpha_checks(sess, aid)
        if checks:
            alpha_checks[aid] = {
                'checks': checks,
                'selfcorr': selfcorr,
                'pass_count': sum(1 for c in checks.values() if c['result'] == 'PASS'),
                'total_checks': len(checks)
            }

        time.sleep(0.3)

    # 标记7-pass候选
    for cand in candidates:
        aid = cand['alpha_id']
        if aid in alpha_checks:
            ac = alpha_checks[aid]
            cand['checks'] = ac['checks']
            cand['selfcorr'] = ac['selfcorr']
            cand['pass_count'] = ac['pass_count']
            cand['total_checks'] = ac['total_checks']

            # 找出失败原因
            failures = [n for n, c in ac['checks'].items() if c['result'] != 'PASS']
            cand['failures'] = failures
        else:
            cand['pass_count'] = 0
            cand['failures'] = ['NOT_CHECKED']

    return candidates, submitted_exprs

def step2_identify_upgrade_candidates(candidates, submitted_exprs):
    """Step 2: 识别需要升阶的候选"""
    print('\n' + '='*60, flush=True)
    print('STEP 2: 识别7-pass升阶候选', flush=True)
    print('='*60, flush=True)

    # 已通过 (8-pass)
    ready_to_submit = []

    # 7-pass (只差self-corr或其他1项)
    seven_pass = []

    # 需要更多工作
    needs_work = []

    for cand in candidates:
        if cand.get('pass_count', 0) < 5:
            continue

        if cand['sharpe'] < 1.25:
            continue

        failures = cand.get('failures', [])
        check_count = cand.get('total_checks', 8)

        if not failures and cand.get('pass_count', 0) == check_count:
            # 8-pass or more
            if cand['sharpe'] >= 1.5 and cand['fitness'] >= 1.0 and cand['turnover'] < 0.6:
                ready_to_submit.append(cand)
        elif len(failures) <= 2 and cand['sharpe'] >= 1.25:
            # 7-pass candidate
            seven_pass.append(cand)
        else:
            if cand['sharpe'] >= 1.5:
                needs_work.append(cand)

    print(f'8-pass (就绪): {len(ready_to_submit)}', flush=True)
    print(f'7-pass (需升阶): {len(seven_pass)}', flush=True)
    print(f'1.5+但多检查失败: {len(needs_work)}', flush=True)

    # 打印7-pass详情
    if seven_pass:
        print(f'\n7-pass 候选详情:', flush=True)
        for cand in sorted(seven_pass, key=lambda x: x['sharpe'], reverse=True)[:20]:
            print(f"  {cand['alpha_id']}: S={cand['sharpe']:.2f} F={cand['fitness']:.2f} "
                  f"TVR={cand['turnover']:.4f} 失败={cand['failures']} "
                  f"自相关={cand.get('selfcorr', '?'):.2f}", flush=True)

    return ready_to_submit, seven_pass, needs_work

def step3_run_upgrades(sess, seven_pass, submitted_exprs):
    """Step 3: 执行升阶"""
    print('\n' + '='*60, flush=True)
    print('STEP 3: 执行升阶', flush=True)
    print('='*60, flush=True)

    upgrade_results = []

    # 选择top 10个7-pass升阶 (S>=1.3 or F>=1.0)
    candidates = [c for c in seven_pass if c['sharpe'] >= 1.3]
    candidates.sort(key=lambda x: x['sharpe'], reverse=True)
    candidates = candidates[:10]

    print(f'选择 {len(candidates)} 个候选升阶', flush=True)

    for cand in candidates:
        aid = cand['alpha_id']
        base_expr = cand['expr']

        if not base_expr:
            print(f'  {aid}: 无表达式, 跳过', flush=True)
            continue

        print(f'\n=== {aid} (S={cand["sharpe"]:.2f}, F={cand["fitness"]:.2f}) ===', flush=True)
        print(f'  失败: {cand["failures"]}', flush=True)

        # 找出自相关导致失败的，重点用rank包装修复
        variants = build_upgrade_variants(base_expr, aid)

        # 优先测试rank包装 (最有效降自相关)
        rank_variants = [v for v in variants if 'rank' in v['strategy']]
        other_variants = [v for v in variants if 'rank' not in v['strategy']]

        ordered_variants = rank_variants + other_variants

        best_result = None
        tested = 0

        for v in ordered_variants[:10]:  # 最多10个变体
            print(f'  -> {v["name"]}', end=' ', flush=True)
            r = simulate_upgrade(sess, v['expr'], v['name'], v['decay'], v['neut'])
            tested += 1

            if r and r.get('sharpe'):
                print(f'S={r["sharpe"]:.3f} F={r["fitness"]:.3f} TVR={r["turnover"]:.3f}', end='', flush=True)

                if r['sharpe'] >= 1.25:
                    # 如果通过阈值, 检查self-corr
                    checks, selfcorr = get_alpha_checks(sess, r['alpha_id'])
                    if checks:
                        failures = [n for n, c in checks.items() if c['result'] != 'PASS']
                        sc_pass = selfcorr is None or selfcorr < 0.7
                        print(f' SC={selfcorr} failures={failures}', end='', flush=True)

                        r['selfcorr'] = selfcorr
                        r['checks_pass'] = len(failures) == 0
                        r['parent'] = aid
                        r['strategy'] = v['strategy']
                        upgrade_results.append(r)

                        if not failures and r['sharpe'] >= 1.5:
                            if not best_result or r['sharpe'] > best_result['sharpe']:
                                best_result = r
                else:
                    print(f' (S<1.25)', end='', flush=True)
            else:
                print(f'FAIL', end='', flush=True)

            print(flush=True)
            time.sleep(3)

        if best_result:
            print(f'  ✓ 最佳: {best_result["name"]} S={best_result["sharpe"]:.2f} F={best_result["fitness"]:.2f}', flush=True)
        else:
            print(f'  ✗ 无通过变体', flush=True)

    print(f'\n升阶完成: 测试 {len(seven_pass)*10} 变体, 通过 {len(upgrade_results)}', flush=True)
    return upgrade_results

def step4_score_and_rank(all_ready, upgrade_results, submitted_exprs):
    """Step 4: 评分排序"""
    print('\n' + '='*60, flush=True)
    print('STEP 4: 评分排序', flush=True)
    print('='*60, flush=True)

    # 合并8-pass + 升阶通过
    combined = []

    for cand in all_ready:
        combined.append({
            **cand,
            'source': '8-pass',
            'total_score': compute_total_score(cand, submitted_exprs)
        })

    for r in upgrade_results:
        if r.get('checks_pass') and r['sharpe'] >= 1.5:
            combined.append({
                'alpha_id': r['alpha_id'],
                'expr': r['expression'],
                'sharpe': r['sharpe'],
                'fitness': r['fitness'],
                'turnover': r['turnover'],
                'selfcorr': r.get('selfcorr'),
                'decay': r.get('decay', 0),
                'parent': r.get('parent', ''),
                'strategy': r.get('strategy', ''),
                'source': 'upgrade',
                'total_score': compute_total_score(r, submitted_exprs)
            })

    # 排序
    combined.sort(key=lambda x: x['total_score'])

    print(f'候选总数: {len(combined)}', flush=True)
    print(f'\n最终排名 (经济逻辑 > 非继承 > 低自相关 > Sharpe > Fitness > Turnover):', flush=True)
    print(f'{"Rank":<5} {"AlphaID":<12} {"Sharpe":<8} {"Fitness":<8} {"TVR":<8} '
          f'{"SelfCorr":<8} {"Score":<6} {"Source":<10} {"Fields":<20}', flush=True)
    print('-'*90, flush=True)

    for i, cand in enumerate(combined):
        fields = extract_base_field(cand.get('expr', ''))
        fields_str = ','.join(fields[:3]) if fields else '?'
        print(f'{i+1:<5} {cand["alpha_id"]:<12} {cand["sharpe"]:<8.2f} {cand["fitness"]:<8.2f} '
              f'{cand["turnover"]:<8.4f} {cand.get("selfcorr", "?"):<8} '
              f'{cand["total_score"]:<6.3f} {cand["source"]:<10} {fields_str:<20}', flush=True)

    return combined

def step5_mark_favorites(sess, ranked):
    """Step 5: 标记Favorite"""
    print('\n' + '='*60, flush=True)
    print('STEP 5: 标记Favorite', flush=True)
    print('='*60, flush=True)

    # 选择top 20
    to_favorite = ranked[:20]

    marked = 0
    for cand in to_favorite:
        aid = cand['alpha_id']
        success = mark_favorite(sess, aid)
        if success:
            marked += 1
            print(f'  ✓ {aid} 标记为favorite', flush=True)
        else:
            print(f'  ✗ {aid} favorite标记失败', flush=True)
        time.sleep(0.5)

    print(f'\n成功标记 {marked}/{len(to_favorite)} 个favorite', flush=True)
    return marked

def step6_final_report(ranked, seven_pass, upgrade_results, all_tested):
    """Step 6: 最终报告"""
    print('\n' + '='*60, flush=True)
    print('STEP 6: 最终汇总报告', flush=True)
    print('='*60, flush=True)

    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_unsubmitted': all_tested + len(seven_pass),
            'eight_pass_ready': len([c for c in ranked if c['source'] == '8-pass']),
            'upgraded_to_eight': len([c for c in ranked if c['source'] == 'upgrade']),
            'seven_pass_remaining': len([c for c in seven_pass if c['sharpe'] >= 1.25]),
            'favorite_marked': len(ranked[:20])
        },
        'top_ranking': [{
            'rank': i+1,
            'alpha_id': c['alpha_id'],
            'score': c['total_score'],
            'sharpe': c['sharpe'],
            'fitness': c['fitness'],
            'turnover': c['turnover'],
            'selfcorr': c.get('selfcorr'),
            'source': c['source'],
            'strategy': c.get('strategy', ''),
            'parent': c.get('parent', ''),
            'expr_preview': c.get('expr', '')[:100],
            'fields': extract_base_field(c.get('expr', ''))
        } for i, c in enumerate(ranked[:50])]
    }

    # 保存
    report_path = OUTPUT_DIR / f'master_upgrade_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f'\n报告已保存: {report_path}', flush=True)

    # 控制台汇总
    print('\n' + '#'*60, flush=True)
    print('#  最终汇总', flush=True)
    print('#'*60, flush=True)
    print(f'总计unsubmitted: {all_tested + len(seven_pass)}', flush=True)
    print(f'8-pass就绪: {report["summary"]["eight_pass_ready"]}', flush=True)
    print(f'升阶后8-pass: {report["summary"]["upgraded_to_eight"]}', flush=True)
    print(f'未升阶7-pass: {report["summary"]["seven_pass_remaining"]}', flush=True)
    print(f'标记Favorite: {report["summary"]["favorite_marked"]}', flush=True)

    # 打印排名
    print('\nTop 20 最终排名:', flush=True)
    for c in report['top_ranking'][:20]:
        print(f"  #{c['rank']:2d} {c['alpha_id']:12s} "
              f"S={c['sharpe']:.2f} F={c['fitness']:.2f} TVR={c['turnover']:.4f} "
              f"SC={c['selfcorr'] or '?'} "
              f"[{c['source']}] {','.join(c['fields'][:3])}", flush=True)

    return report

# ============================================================
# Main
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Alpha Master Upgrade Pipeline')
    parser.add_argument('--mode', type=str, default='full',
                        choices=['full', 'rank-only', 'favorite-only'])
    parser.add_argument('--pass-sharpe', type=float, default=1.5)
    args = parser.parse_args()

    global PASS_SHARPE
    PASS_SHARPE = args.pass_sharpe

    print('='*60, flush=True)
    print('Alpha Master Upgrade Pipeline', flush=True)
    print(f'Mode: {args.mode}', flush=True)
    print(f'Pass Sharpe: {PASS_SHARPE}', flush=True)
    print('='*60, flush=True)

    # Login
    sess = login()
    if not sess:
        print('登录失败!', flush=True)
        return

    # Get submitted exprs for inheritance check
    submitted_exprs = fetch_submitted_exprs(sess)
    print(f'已加载 {len(submitted_exprs)} 个已提交alpha表达式', flush=True)

    if args.mode == 'favorite-only':
        # 只从现有候选加载和标记favorite
        print('\n[Favorite Only Mode]', flush=True)
        candidates, _ = step1_gather_candidates(sess)
        ready, seven, _ = step2_identify_upgrade_candidates(candidates, submitted_exprs)

        print(f'\n就绪: {len(ready)}, 7-pass: {len(seven)}', flush=True)

        all_ready = []
        for c in ready:
            all_ready.append({
                'alpha_id': c['alpha_id'],
                'expr': c['expr'],
                'sharpe': c['sharpe'],
                'fitness': c['fitness'],
                'turnover': c['turnover'],
                'selfcorr': c.get('selfcorr'),
            })

        ranked = step4_score_and_rank(all_ready, [], submitted_exprs)
        step5_mark_favorites(sess, ranked)
        step6_final_report(ranked, seven, [], len(ready))
        return

    if args.mode == 'rank-only':
        candidates, _ = step1_gather_candidates(sess)
        ready, seven, _ = step2_identify_upgrade_candidates(candidates, submitted_exprs)
        all_ready = []
        for c in ready:
            all_ready.append({
                'alpha_id': c['alpha_id'],
                'expr': c['expr'],
                'sharpe': c['sharpe'],
                'fitness': c['fitness'],
                'turnover': c['turnover'],
                'selfcorr': c.get('selfcorr'),
            })
        ranked = step4_score_and_rank(all_ready, [], submitted_exprs)
        step6_final_report(ranked, seven, [], len(ready))
        return

    # Full pipeline
    candidates, submitted_exprs = step1_gather_candidates(sess)
    ready, seven, needs_work = step2_identify_upgrade_candidates(candidates, submitted_exprs)

    # Build 8-pass list
    all_ready_list = []
    for c in ready:
        all_ready_list.append({
            'alpha_id': c['alpha_id'],
            'expr': c['expr'],
            'sharpe': c['sharpe'],
            'fitness': c['fitness'],
            'turnover': c['turnover'],
            'selfcorr': c.get('selfcorr'),
        })

    # Run upgrades on 7-pass
    upgrade_results = []
    if seven:
        upgrade_results = step3_run_upgrades(sess, seven, submitted_exprs)

    # Score and rank
    ranked = step4_score_and_rank(all_ready_list, upgrade_results, submitted_exprs)

    # Mark favorites
    step5_mark_favorites(sess, ranked)

    # Final report
    step6_final_report(ranked, seven, upgrade_results, len(all_ready_list))

    print('\n' + '='*60, flush=True)
    print('Pipeline Complete!', flush=True)
    print('='*60, flush=True)

if __name__ == '__main__':
    main()
