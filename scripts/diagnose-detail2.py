#!/usr/bin/env python3
"""Diagnose submit block - properly accept cookies then get alpha detail"""

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

        # Accept cookies properly
        print("\n=== Accepting cookies ===")
        page.wait_for_timeout(2000)

        # Try multiple times to accept
        for i in range(3):
            try:
                accept_btn = page.locator('button:has-text("Accept All")')
                if accept_btn.count() > 0:
                    accept_btn.first.click()
                    print("Clicked 'Accept All'")
                    page.wait_for_timeout(1000)
                    break
            except Exception as e:
                print(f"Attempt {i+1} failed: {e}")
                page.wait_for_timeout(1000)

        # Skip wizard if any
        try:
            skip_btn = page.locator('button:has-text("Skip")')
            if skip_btn.count() > 0:
                skip_btn.first.click()
                print("Clicked 'Skip'")
                page.wait_for_timeout(2000)
        except:
            pass

        # Now navigate to d5nbrQ5J
        print("\n=== Navigating to d5nbrQ5J ===")
        page.goto("https://platform.worldquantbrain.com/alphas/d5nbrQ5J",
                  wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(8000)

        print(f"URL: {page.url}")

        # Get page content
        body_text = page.evaluate("document.body.innerText")
        print(f"Body length: {len(body_text)}")

        if len(body_text) < 100:
            print("Page body is nearly empty - likely cookie modal blocking")
            # Try waiting more
            page.wait_for_timeout(5000)

        body_text = page.evaluate("document.body.innerText")
        print(f"Body length after wait: {len(body_text)}")

        # Check for key elements
        print(f"\nHas 'Sharpe': {'Sharpe' in body_text}")
        print(f"Has 'Fitness': {'Fitness' in body_text}")
        print(f"Has 'Submit': {'Submit' in body_text}")
        print(f"Has 'PENDING': {'PENDING' in body_text}")

        # Get first 3000 chars
        print(f"\nBody text (first 3000 chars):\n{body_text[:3000]}")

        # Find buttons
        buttons = page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button'));
            return btns.filter(b => b.textContent.trim()).map(b => b.textContent.trim());
        }""")

        print(f"\nButtons with text ({len(buttons)}): {buttons[:20]}")

        # Screenshot
        screenshot = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/d5nbrQ5J-detail.png'
        page.screenshot(path=screenshot)
        print(f"\nScreenshot: {screenshot}")

        browser.close()

if __name__ == '__main__':
    main()