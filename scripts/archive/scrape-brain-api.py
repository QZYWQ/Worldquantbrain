#!/usr/bin/env python3
"""Scrape BRAIN - use API directly with fetch"""

import json

CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt'

def main():
    from playwright.sync_api import sync_playwright

    creds = json.load(open(CRED_FILE))

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=False)
        context = browser.new_context(viewport={"width": 1440, "height": 1200})
        page = context.new_page()

        # Login first
        print("Going to sign-in...")
        page.goto("https://platform.worldquantbrain.com/sign-in",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        page.fill('input[type="email"], input[name="email"]', creds[0])
        page.wait_for_timeout(300)
        page.fill('input[type="password"]', creds[1])
        page.wait_for_timeout(300)
        page.click('button[type="submit"]')
        page.wait_for_timeout(10000)

        print("After login URL:", page.url)

        # Accept cookies and skip wizard
        try:
            page.click('button:has-text("Accept All")', timeout=3000)
            page.wait_for_timeout(1000)
        except:
            pass

        try:
            page.click('button:has-text("Skip")', timeout=3000)
            page.wait_for_timeout(2000)
        except:
            pass

        # Navigate to unsubmitted
        page.goto("https://platform.worldquantbrain.com/alphas/unsubmitted",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(20000)

        print("Final URL:", page.url)

        # Get the API response directly from page context
        print("\n=== Fetching API data via page.evaluate ===")

        api_data = page.evaluate("""async () => {
            // Try to get the alpha list from the API
            try {
                // First check if there's a fetch happening to the alphas endpoint
                const response = await fetch('/api/users/self/alphas?status=UNSUBMITTED&limit=100', {
                    credentials: 'include'
                });
                const text = await response.text();
                return { status: response.status, ok: response.ok, text: text.substring(0, 10000) };
            } catch(e) {
                return { error: e.message };
            }
        }""")

        print("API Response:", json.dumps(api_data, indent=2))

        # Try different API endpoints
        endpoints = [
            '/api/users/self/alphas?status=UNSUBMITTED',
            '/api/alphas?status=UNSUBMITTED',
            '/api/users/self/alphas',
        ]

        for endpoint in endpoints:
            print(f"\n=== Trying {endpoint} ===")
            result = page.evaluate(f"""async () => {{
                try {{
                    const response = await fetch('{endpoint}', {{ credentials: 'include' }});
                    const text = await response.text();
                    return {{ status: response.status, ok: response.ok, text: text.substring(0, 5000) }};
                }} catch(e) {{
                    return {{ error: e.message }};
                }}
            }}""")
            print(f"Status: {result.get('status')}, OK: {result.get('ok')}")
            if result.get('text'):
                print(f"Response: {result.get('text')[:2000]}")

        # Screenshot
        screenshot_path = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/screenshot-api.png'
        page.screenshot(path=screenshot_path, full_page=True)
        print("\nScreenshot:", screenshot_path)

        # Save
        output = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/brain-unsubmitted-api.json'
        with open(output, 'w') as f:
            json.dump({
                "scraped_at": "2026-05-17T09:00:00Z",
                "url": page.url,
                "api_data": api_data
            }, f, indent=2, ensure_ascii=False)
        print("Saved to:", output)

        browser.close()

if __name__ == '__main__':
    main()
