#!/usr/bin/env python3
"""Check if alpha page loads or if it redirects"""

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

        # Accept cookies
        try:
            page.click('button:has-text("Accept All")', timeout=3000)
        except:
            pass

        # Skip wizard
        try:
            page.click('button:has-text("Skip")', timeout=3000)
        except:
            pass

        # Try different navigation approaches
        print("\n=== Test 1: Direct navigate ===")
        page.goto("https://platform.worldquantbrain.com/alphas/1YoX2GxX",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)

        print(f"URL after direct: {page.url}")

        # Check if we're on the right page
        body = page.evaluate("document.body.innerText")
        print(f"Body length: {len(body)}")

        if "/alphas/1YoX2GxX" not in page.url:
            print("REDIRECTED from alpha page!")

        # Try simulating the alpha directly via API
        print("\n=== Test 2: Check via API ===")
        api_check = page.evaluate("""async () => {
            const resp = await fetch('https://api.worldquantbrain.com/alphas/1YoX2GxX', {
                credentials: 'include'
            });
            const data = await resp.json();
            return {
                status: resp.status,
                id: data.id,
                code: data.regular?.code,
                sharpe: data.is?.sharpe,
                fitness: data.is?.fitness,
                tags: data.tags,
                selfCorrCheck: data.is?.checks?.find(c => c.name === 'SELF_CORRELATION')
            };
        }""")

        print(f"API Check: {json.dumps(api_check, indent=2)}")

        # Screenshot
        screenshot = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/alpha-redirect-check.png'
        page.screenshot(path=screenshot, full_page=True)
        print(f"\nScreenshot: {screenshot}")

        browser.close()

if __name__ == '__main__':
    main()