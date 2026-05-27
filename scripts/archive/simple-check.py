#!/usr/bin/env python3
"""Simple check - just take screenshot and see what's on page"""

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

        # Navigate to alpha page
        print("\n=== Going to alpha page ===")
        page.goto("https://platform.worldquantbrain.com/alphas/1YoX2GxX",
                  wait_until="domcontentloaded", timeout=30000)

        # Just wait 30 seconds and see if page loads
        print("Waiting 30 seconds for page to load...")
        page.wait_for_timeout(30000)

        # Take screenshot
        screenshot = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/loading-check.png'
        page.screenshot(path=screenshot)
        print(f"Screenshot: {screenshot}")

        # Get page title and some text
        title = page.title()
        body_text = page.evaluate("document.body?.innerText || ''")
        print(f"Title: {title}")
        print(f"Body length: {len(body_text)}")
        print(f"Body preview: {body_text[:500]}")

        browser.close()

if __name__ == '__main__':
    main()