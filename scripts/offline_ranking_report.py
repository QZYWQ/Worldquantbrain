#!/usr/bin/env python3
"""
离线Alpha排名报告 — 基于缓存数据分析
无需API连接即可生成完整的评分排序
"""
import json
from pathlib import Path
from datetime import datetime

# ============================================================
# 已提交alpha — 用于检测继承
# ============================================================
SUBMITTED_IDS = [
    'O0bXoVV1','LLgOWZmn','88Ob79jV','GrnExm2Q','e7dPWeop',
    'A1gVE97w','bloqmdJK','A1g6AlWg','Xg2X2jxl','E5g7vMjJ',
    'E5repQ81','d5l07rpX','gJmojOQm','0mAE3qzp','1YodbWO6',
    '2rvNV1qJ','RRNmMErj','1YopVrdW','xAeN6jGp','1YoX2GxX','QPn0vn3X'
]

# KILLED family — 已确认结构性问题, 不应再挖掘
KILLED_FAMILIES = [
    'ts_decay_linear',
    'ts_corr(close,volume',
    'ts_std_dev(returns',
    'volume/ts_mean(volume',
    'ts_rank(earnings',
]

# 经济逻辑优先级
ECON_PRIORITY_MAP = {
    'fundamental': 1,  # 财务/基本面
    'analyst': 1,      # 分析师预期
    'sentiment': 2,    # 情绪指标
    'price_volume': 3, # 价量
    'derived': 4,      # 衍生指标
    'model': 5,        # 模型复合
}

# ============================================================
def classify_economic_logic(expr):
    """分类经济逻辑类型"""
    expr_l = expr.lower()

    # Fundamental
    if any(k in expr_l for k in ['fnd6_','anl4_','earnings','revenue','sales',
                                   'eps','profit','income','equity','assets',
                                   'debt','liability','tobins','fn_comp',
                                   'fn_interest','dividend','book_value',
                                   'cashflow','margin','roe','roa',
                                   'current_accrued','current_liabilities']):
        return 'fundamental'
    # Analyst
    if any(k in expr_l for k in ['anl4_','analyst','afv4','af_eps']):
        return 'analyst'
    # Sentiment/Buzz
    if any(k in expr_l for k in ['scl12','sentiment','buzz','news','nws','mws']):
        return 'sentiment'
    # Price/Volume
    if any(k in expr_l for k in ['close','volume','open','high','low','vwap','returns']):
        return 'price_volume'
    # Derived
    if any(k in expr_l for k in ['unsystematic','hvol','pcr','vsm','pcr_oi',
                                   'breakeven','snt1','growth_potential',
                                   'multi_factor','rp_css']):
        return 'derived'
    # Model
    if any(k in expr_l for k in ['mdl','model','model51','model77','risk']):
        return 'model'

    return 'price_volume'  # default

def is_in_killed_family(expr):
    """检查是否属于已KILL的家族"""
    expr_s = expr.replace(' ', '')
    for killed in KILLED_FAMILIES:
        if killed in expr_s:
            return True
    return False

def extract_fields(expr):
    """提取表达式中使用的data field"""
    fields = []
    known_prefixes = ['fnd6_','anl4_','mdl','scl12_','nws','mws',
                      'tobins_','earnings_','revenue_','sales_',
                      'fn_comp','fn_interest','unsystematic_',
                      'growth_potential','multi_factor',
                      'close','volume','returns','vwap','high','low',
                      'cap','assets','rp_css','pcr_oi','vsm3',
                      'hvol_20','breakeven','snt1']
    for p in known_prefixes:
        if p in expr.lower():
            fields.append(p)
    return list(set(fields))

def inheritance_score(expr, submitted_exprs):
    """计算继承性得分 (0=独立, 1=略微继承, 2=高度继承)"""
    expr_s = expr.replace(' ', '')
    for sub_expr in submitted_exprs:
        sub_s = sub_expr.replace(' ', '')
        # Check long common substring
        common = longest_common_substring(expr_s, sub_s)
        if common and len(common) > 30:
            return 2
    return 0

def longest_common_substring(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    longest = ''
    for i in range(len(s1)):
        for j in range(i + len(longest) + 1, len(s1) + 1):
            if s1[i:j] in s2:
                longest = s1[i:j]
    return longest if len(longest) > 5 else ''

def compute_score(alpha, submitted_exprs):
    """综合评分 (越低越好)"""
    expr = alpha.get('expression', '')
    sharpe = alpha.get('sharpe', 0) or 0
    fitness = alpha.get('fitness', 0) or 0
    turnover = alpha.get('turnover', 0) or 0

    # 经济逻辑 (30%)
    econ_type = classify_economic_logic(expr)
    econ_priority = ECON_PRIORITY_MAP.get(econ_type, 5)
    norm_econ = (econ_priority - 1) / 4

    # 非继承 (20%)
    inherit = inheritance_score(expr, submitted_exprs)
    norm_inherit = inherit / 2

    # 非KILLED家族 (10%)
    killed = 1 if is_in_killed_family(expr) else 0

    # Sharpe (20%)
    norm_sharpe = max(0, min(1, (1.5 - min(sharpe, 4.0)) / 2.5))

    # Fitness (10%)
    norm_fitness = max(0, min(1, (1.0 - min(fitness, 3.0)) / 2.0))

    # Turnover (10%)
    norm_turnover = max(0, min(1, turnover / 0.6))

    total = (
        norm_econ * 0.30 +
        norm_inherit * 0.20 +
        killed * 0.10 +
        norm_sharpe * 0.20 +
        norm_fitness * 0.10 +
        norm_turnover * 0.10
    )

    return total

# ============================================================
# Main
# ============================================================

def main():
    base = Path('/Users/zpdedn/Documents/project/Worldquantbrain')
    capture_dir = base / 'runs' / 'simulation-captures'

    # Load cached unsubmitted data
    cache_path = capture_dir / 'unsubmitted-full-2026-05-20T19-02-51-888Z.json'
    with open(cache_path) as f:
        data = json.load(f)

    all_alphas = data['alphas']
    print(f'Loaded {len(all_alphas)} cached unsubmitted alphas')

    # Load top candidates list for expression data
    top_path = capture_dir / 'top-candidates-2026-05-21.json'
    with open(top_path) as f:
        top_candidates = json.load(f)
    top_map = {c['alphaId']: c['expression'] for c in top_candidates}
    print(f'Loaded {len(top_candidates)} top candidates with expressions')

    # Also load promising-alpha-details for more expressions
    prom_path = capture_dir / 'promising-alpha-details-2026-05-21.json'
    if prom_path.exists():
        with open(prom_path) as f:
            prom_data = json.load(f)
        if isinstance(prom_data, list):
            for c in prom_data:
                top_map[c.get('alphaId', '')] = c.get('expression', c.get('regular', {}).get('code', ''))
        elif isinstance(prom_data, dict):
            for k, v in prom_data.items():
                if isinstance(v, dict) and v.get('expression'):
                    top_map[k] = v['expression']

    # Load submitted alpha expressions from memory
    sub_exprs_path = list(capture_dir.glob('may19_upgrade_final.json'))

    # Enrich unsubmitted data with expressions from top candidates
    for a in all_alphas:
        aid = a['alphaId']
        if aid in top_map and not a.get('expression'):
            a['expression'] = top_map[aid]

    # Filter candidates
    candidates = []
    for a in all_alphas:
        s = a.get('sharpe', 0) or 0
        f = a.get('fitness', 0) or 0
        t = a.get('turnover', 0) or 0

        if s >= 1.25 and f >= 1.0 and t < 0.6:
            expr = a.get('expression', '')
            if not expr:
                continue  # skip if no expression
            candidates.append(a)

    print(f'Candidates with S>=1.25, F>=1.0, TVR<0.6: {len(candidates)}')

    # Score & rank
    submitted_exprs = []  # We don't have all submitted expressions offline
    scored = []

    for a in candidates:
        score = compute_score(a, submitted_exprs)
        econ = classify_economic_logic(a.get('expression', ''))
        fields = extract_fields(a.get('expression', ''))
        killed = is_in_killed_family(a.get('expression', ''))

        scored.append({
            'alpha_id': a['alphaId'],
            'sharpe': a['sharpe'],
            'fitness': a['fitness'],
            'turnover': a['turnover'],
            'expression': a.get('expression', '')[:100],
            'econ_type': econ,
            'econ_priority': ECON_PRIORITY_MAP.get(econ, 5),
            'is_killed': killed,
            'fields': fields,
            'score': score
        })

    # Sort by score
    scored.sort(key=lambda x: (x['score'], -x['sharpe']))

    # ============================================================
    # Generate Report
    # ============================================================
    print('\n' + '='*80)
    print('ALPHA RANKING REPORT — OFFLINE ANALYSIS')
    print(f'Generated: {datetime.now().isoformat()}')
    print(f'API Status: LOCKED (using cached data from 2026-05-20)')
    print('='*80)

    # Summary
    total = len(scored)
    killed_count = sum(1 for c in scored if c['is_killed'])
    live_count = total - killed_count
    print(f'\nTotal candidates: {total}')
    print(f'KILLED families: {killed_count}')
    print(f'LIVE candidates: {live_count}')

    # By economic type
    print(f'\n--- By Economic Logic ---')
    by_econ = {}
    for c in scored:
        if not c['is_killed']:
            by_econ.setdefault(c['econ_type'], []).append(c)
    for etype, cands in sorted(by_econ.items(), key=lambda x: min(c['econ_priority'] for c in x[1])):
        print(f'  {etype:20s} ({ECON_PRIORITY_MAP.get(etype, 5)}): {len(cands)} candidates')

    # Top LIVE candidates
    live_scored = [c for c in scored if not c['is_killed']]

    print(f'\n' + '='*80)
    print('TOP 30 LIVE CANDIDATES (KILLED families excluded)')
    print(f'{"Rank":<5} {"AlphaID":<12} {"Sharpe":<8} {"Fitness":<8} {"TVR":<8} {"Score":<6} {"Econ":<18} {"Fields":<25}')
    print('-'*80)

    for i, c in enumerate(live_scored[:30]):
        fields_str = ','.join(c['fields'][:2]) if c['fields'] else '?'
        print(f'{i+1:<5} {c["alpha_id"]:<12} {c["sharpe"]:<8.2f} {c["fitness"]:<8.2f} '
              f'{c["turnover"]:<8.4f} {c["score"]:<6.3f} {c["econ_type"]:<18} {fields_str:<25}')

    # High Sharpe >2.0 candidates
    print(f'\n' + '='*80)
    print('HIGH SHARPE (S>2.0) — all with expressions')
    high_sharpe = [c for c in scored if c['sharpe'] >= 2.0]
    print(f'{"AlphaID":<12} {"Sharpe":<8} {"Fitness":<8} {"TVR":<8} {"Score":<6} {"Killed":<8} Expr')
    print('-'*80)
    for c in high_sharpe:
        expr = c['expression'][:50]
        print(f'{c["alpha_id"]:<12} {c["sharpe"]:<8.2f} {c["fitness"]:<8.2f} {c["turnover"]:<8.4f} '
              f'{c["score"]:<6.3f} {"KILL" if c["is_killed"] else "LIVE":<8} {expr}')

    # Economic priority order
    print(f'\n' + '='*80)
    print('RANKED BY ECONOMIC LOGIC (LIVE only, fundamental first)')
    print(f'{"Rank":<5} {"AlphaID":<12} {"Sharpe":<8} {"Fitness":<8} {"TVR":<8} {"Econ":<18} {"Fields":<25}')
    print('-'*80)
    econ_sorted = sorted(live_scored, key=lambda x: (x['econ_priority'], -x['sharpe']))
    for i, c in enumerate(econ_sorted[:30]):
        fields_str = ','.join(c['fields'][:2]) if c['fields'] else '?'
        print(f'{i+1:<5} {c["alpha_id"]:<12} {c["sharpe"]:<8.2f} {c["fitness"]:<8.2f} '
              f'{c["turnover"]:<8.4f} {c["econ_type"]:<18} {fields_str:<25}')

    # ============================================================
    # Save report
    # ============================================================
    report = {
        'generated_at': datetime.now().isoformat(),
        'api_status': 'LOCKED',
        'data_source': str(cache_path),
        'summary': {
            'total_unsubmitted': len(all_alphas),
            'total_candidates': total,
            'killed_family': killed_count,
            'live_candidates': live_count,
            'by_economic_logic': {e: len(c) for e, c in by_econ.items()},
        },
        'top_30_live': [{
            'rank': i+1, 'alpha_id': c['alpha_id'],
            'sharpe': c['sharpe'], 'fitness': c['fitness'],
            'turnover': c['turnover'], 'score': c['score'],
            'econ_type': c['econ_type'], 'fields': c['fields']
        } for i, c in enumerate(live_scored[:30])],
        'high_sharpe': [{
            'alpha_id': c['alpha_id'], 'sharpe': c['sharpe'],
            'fitness': c['fitness'], 'is_killed': c['is_killed']
        } for c in high_sharpe[:20]],
        'all_live_candidates': [{
            'alpha_id': c['alpha_id'], 'sharpe': c['sharpe'],
            'fitness': c['fitness'], 'turnover': c['turnover'],
            'score': c['score'], 'econ_type': c['econ_type'],
            'fields': c['fields'], 'is_killed': c['is_killed'],
            'expression': c['expression']
        } for c in scored[:100]]
    }

    report_path = base / 'runs' / 'candidate-batches' / f'offline-ranking-report-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f'\nReport saved: {report_path}')

if __name__ == '__main__':
    main()
