#!/usr/bin/env python3
"""Try to trigger self-correlation check for blocked alphas"""

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

        print("Logged in")

        # For each alpha with ace_tag, try to trigger self-correlation check
        # and check if there's a way to remove the tag or bypass

        alpha_ids = ['1YoX2GxX', 'd5nbrQ5J', 'ZYjARRL3']

        for alpha_id in alpha_ids:
            print(f"\n{'='*60}")
            print(f"Checking {alpha_id}")

            # Get full alpha details
            result = page.evaluate(f"""async () => {{
                try {{
                    const response = await fetch('https://api.worldquantbrain.com/alphas/{alpha_id}', {{
                        credentials: 'include'
                    }});
                    const text = await response.text();
                    return JSON.parse(text);
                }} catch(e) {{
                    return {{ error: e.message }};
                }}
            }}""")

            if isinstance(result, dict):
                print(f"  Status: {result.get('status')}")
                print(f"  Tags: {result.get('tags')}")
                print(f"  Grade: {result.get('grade')}")
                print(f"  Stage: {result.get('stage')}")

                is_data = result.get('is', {})
                if is_data:
                    checks = is_data.get('checks', [])
                    for check in checks:
                        if 'SELF_CORRELATION' in check.get('name', ''):
                            print(f"  SELF_CORRELATION: {check}")

                # Check if there's a simulate endpoint to trigger re-check
                print(f"\n  Trying to trigger simulation for self-correlation check...")

                sim_result = page.evaluate(f"""async () => {{
                    try {{
                        // Try to fetch the alpha with view mode to get submission info
                        const viewResp = await fetch('https://platform.worldquantbrain.com/alphas/{alpha_id}', {{
                            credentials: 'include'
                        }});
                        return {{ status: viewResp.status, url: viewResp.url }};
                    }} catch(e) {{
                        return {{ error: e.message }};
                    }}
                }}""")

                print(f"  View response: {sim_result}")

        # Now check if there's an endpoint to remove ace_tag
        print("\n\n=== Checking for tag removal API ===")

        for alpha_id in alpha_ids:
            # Try to PATCH the alpha to remove tags
            patch_result = page.evaluate(f"""async () => {{
                try {{
                    const response = await fetch('https://api.worldquantbrain.com/alphas/{alpha_id}', {{
                        method: 'PATCH',
                        credentials: 'include',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ tags: [] }})
                    }});
                    const text = await response.text();
                    return {{ status: response.status, text: text.substring(0, 1000) }};
                }} catch(e) {{
                    return {{ error: e.message }};
                }}
            }}""")

            print(f"\n{alpha_id} PATCH result: {patch_result}")

        browser.close()

if __name__ == '__main__':
    main()