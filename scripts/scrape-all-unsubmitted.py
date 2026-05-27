#!/usr/bin/env python3
"""Get all unsubmitted alphas from BRAIN API"""

import json

CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt'

def main():
    from playwright.sync_api import sync_playwright

    creds = json.load(open(CRED_FILE))

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=False)
        context = browser.new_context(viewport={"width": 1440, "height": 1200})
        page = context.new_page()

        # Login
        print("Logging in...")
        page.goto("https://platform.worldquantbrain.com/sign-in",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        page.fill('input[type="email"], input[name="email"]', creds[0])
        page.wait_for_timeout(300)
        page.fill('input[type="password"]', creds[1])
        page.wait_for_timeout(300)
        page.click('button[type="submit"]')
        page.wait_for_timeout(10000)

        # Accept cookies
        try:
            page.click('button:has-text("Accept All")', timeout=3000)
            page.wait_for_timeout(1000)
        except:
            pass

        print("Logged in, fetching all unsubmitted alphas...")

        # Fetch all with pagination
        all_alphas = []
        offset = 0
        limit = 50

        while True:
            print(f"\nFetching offset={offset}...")
            result = page.evaluate(f"""async () => {{
                try {{
                    const response = await fetch('https://api.worldquantbrain.com/users/self/alphas?status=UNSUBMITTED&limit={limit}&offset={offset}', {{
                        credentials: 'include'
                    }});
                    const text = await response.text();
                    return {{ status: response.status, ok: response.ok, text }};
                }} catch(e) {{
                    return {{ error: e.message }};
                }}
            }}""")

            if result.get('error') or not result.get('ok'):
                print(f"Error fetching: {result}")
                break

            try:
                data = json.loads(result['text'])
                results = data.get('results', [])
                print(f"Got {len(results)} alphas")

                if not results:
                    break

                all_alphas.extend(results)

                next_url = data.get('next')
                if not next_url:
                    break

                offset += limit

                # Safety limit
                if offset > 5000:
                    print("Safety limit reached")
                    break

            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
                break

        print(f"\n\nTotal unsubmitted alphas: {len(all_alphas)}")

        # Filter for interesting ones (Sharpe > 0.8 or Fitness > 0.8)
        interesting = []
        for a in all_alphas:
            is_data = a.get('is', {})
            sharpe = is_data.get('sharpe', 0) or 0
            fitness = is_data.get('fitness', 0) or 0
            code = a.get('regular', {}).get('code', '')
            alpha_id = a.get('id', '')
            date_created = a.get('dateCreated', '')

            # Only include if has real metrics and interesting metrics
            if sharpe != 0 or fitness != 0:
                interesting.append({
                    'id': alpha_id,
                    'code': code,
                    'sharpe': round(sharpe, 2) if sharpe else 0,
                    'fitness': round(fitness, 2) if fitness else 0,
                    'turnover': round(is_data.get('turnover', 0) or 0, 4),
                    'returns': round(is_data.get('returns', 0) or 0, 4),
                    'longCount': is_data.get('longCount', 0),
                    'shortCount': is_data.get('shortCount', 0),
                    'checks': [c.get('name') for c in is_data.get('checks', []) if c.get('result') == 'FAIL'],
                    'dateCreated': date_created[:10] if date_created else ''
                })

        # Sort by fitness descending
        interesting.sort(key=lambda x: x['fitness'], reverse=True)

        print(f"\nInteresting alphas (non-zero metrics): {len(interesting)}")
        print("\nTop 50 by fitness:")
        for i, a in enumerate(interesting[:50]):
            print(f"{i+1}. {a['id']} S={a['sharpe']} F={a['fitness']} TVR={a['turnover']} R={a['returns']} | {a['code'][:80]}")

        # Save full data
        output = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/brain-unsubmitted-all.json'
        with open(output, 'w') as f:
            json.dump({
                "scraped_at": "2026-05-17T11:00:00Z",
                "total_count": len(all_alphas),
                "interesting_count": len(interesting),
                "alphas": all_alphas,
                "interesting": interesting
            }, f, indent=2, ensure_ascii=False)
        print(f"\nSaved to: {output}")

        browser.close()

if __name__ == '__main__':
    main()
