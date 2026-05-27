#!/usr/bin/env python3
"""Diagnose alpha submission block - check API and page state"""

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

        # Check alpha status via API
        print("\n=== Checking alpha status via API ===")

        for alpha_id in ['1YoX2GxX', 'd5nbrQ5J', 'ZYjARRL3']:
            result = page.evaluate(f"""async () => {{
                try {{
                    const response = await fetch('https://api.worldquantbrain.com/alphas/{alpha_id}', {{
                        credentials: 'include'
                    }});
                    const text = await response.text();
                    return {{ status: response.status, text: text.substring(0, 5000) }};
                }} catch(e) {{
                    return {{ error: e.message }};
                }}
            }}""")

            print(f"\n{alpha_id} API Status: {result.get('status')}")
            if result.get('text'):
                try:
                    data = json.loads(result['text'])
                    print(f"  Keys: {list(data.keys())}")
                    for key in ['status', 'tags', 'classifications', 'grade', 'stage', 'message', 'error', 'detail']:
                        if key in data:
                            print(f"  {key}: {data[key]}")
                except:
                    print(f"  Raw: {result.get('text')[:300]}")

        # Navigate to alphas page
        print("\n\n=== Navigating to alphas page ===")
        page.goto("https://platform.worldquantbrain.com/alphas/unsubmitted",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(10000)

        print(f"URL: {page.url()}")

        # Get page state
        page_state = page.evaluate("""() => {
            // Find our alphas
            const body = document.body.innerText;
            return {
                url: window.location.href,
                has1YoX2GxX: body.includes('1YoX2GxX'),
                hasd5nbrQ5J: body.includes('d5nbrQ5J'),
                hasZYjARRL3: body.includes('ZYjARRL3'),
                bodySnippet: body.substring(0, 2000)
            };
        }""")

        print(f"Found 1YoX2GxX: {page_state['has1YoX2GxX']}")
        print(f"Found d5nbrQ5J: {page_state['hasd5nbrQ5J']}")
        print(f"Found ZYjARRL3: {page_state['hasZYjARRL3']}")
        print(f"\nBody snippet:\n{page_state['bodySnippet'][:1500]}")

        # Screenshot
        screenshot_path = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/submit-blocked.png'
        page.screenshot(path=screenshot_path, fullPage=True)
        print(f"\nScreenshot: {screenshot_path}")

        # Check for any modal or overlay that might block click
        modal_check = page.evaluate("""() => {
            const modals = document.querySelectorAll('[class*="modal"], [class*="overlay"], [class*="dialog"]');
            return {
                modalCount: modals.length,
                modalTexts: Array.from(modals).map(m => m.textContent?.substring(0, 100))
            };
        }""")

        print(f"\nModals/overlays: {modal_check['modalCount']}")
        if modal_check['modalTexts']:
            print(f"Modal contents: {modal_check['modalTexts']}")

        browser.close()

if __name__ == '__main__':
    main()