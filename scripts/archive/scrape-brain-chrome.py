#!/usr/bin/env python3
"""Scrape BRAIN - use Chrome profile with existing session"""

import json
import os
import glob

CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt'
# Try to find Chrome cookies
CHROME_COOKIES_PATH = os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/Cookies')

def main():
    from playwright.sync_api import sync_playwright

    creds = json.load(open(CRED_FILE))

    # First try using Chrome profile
    print("Trying Chrome profile approach...")
    try:
        # Copy Chrome profile for persistence
        import shutil
        cache_dir = '/private/tmp/wqb-brain-session'
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
        os.makedirs(cache_dir, exist_ok=True)

        with sync_playwright() as p:
            browser = p.chromium.launch(channel='chrome', headless=False)
            context = browser.new_context(
                viewport={"width": 1440, "height": 1200},
                storage_state=None  # Don't use existing state
            )
            page = context.new_page()

            # Login
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

            # Accept cookies
            try:
                page.click('button:has-text("Accept All")', timeout=3000)
                page.wait_for_timeout(1000)
            except:
                pass

            # Skip wizard
            try:
                page.click('button:has-text("Skip")', timeout=3000)
                page.wait_for_timeout(2000)
            except:
                pass

            # Navigate to unsubmitted
            print("\nNavigating to unsubmitted...")
            page.goto("https://platform.worldquantbrain.com/alphas/unsubmitted",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(20000)

            print("Final URL:", page.url)

            # Get all text
            body = page.evaluate("document.body?.innerText || ''")
            print("\nBody text (first 5000 chars):")
            print(body[:5000])

            # Check for any API calls made by the page
            api_calls = page.evaluate("""() => {
                // Check performance entries for XHR
                const entries = window.performance?.getEntriesByType?.('resource') || [];
                return entries
                    .filter(e => e.initiatorType === 'xmlhttprequest' || e.name.includes('api'))
                    .slice(0, 20)
                    .map(e => ({ url: e.name, status: e.responseStatus, type: e.initiatorType }));
            }""")

            print("\nAPI calls:", json.dumps(api_calls, indent=2))

            # Screenshot
            screenshot_path = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/screenshot-chrome.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print("\nScreenshot:", screenshot_path)

            # Save
            output = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/brain-unsubmitted-chrome.json'
            with open(output, 'w') as f:
                json.dump({
                    "scraped_at": "2026-05-17T08:00:00Z",
                    "url": page.url,
                    "body_text": body,
                    "api_calls": api_calls
                }, f, indent=2, ensure_ascii=False)
            print("Saved to:", output)

            browser.close()
    except Exception as e:
        print(f"Chrome profile failed: {e}")
        print("\nTrying without Chrome channel...")

        # Fallback to regular browser
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(viewport={"width": 1440, "height": 1200})
            page = context.newPage()

            # Login
            page.goto("https://platform.worldquantbrain.com/sign-in",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)

            page.fill('input[type="email"], input[name="email"]', creds[0])
            page.wait_for_timeout(300)
            page.fill('input[type="password"]', creds[1])
            page.wait_for_timeout(300)
            page.click('button[type="submit"]')
            page.wait_for_timeout(15000)

            print("After login URL:", page.url)

            # Navigate
            page.goto("https://platform.worldquantbrain.com/alphas/unsubmitted",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(20000)

            print("Final URL:", page.url)
            body = page.evaluate("document.body?.innerText || ''")
            print("\nBody text:", body[:5000])

            screenshot_path = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/screenshot-fallback.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print("Screenshot:", screenshot_path)

            output = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/brain-unsubmitted-fallback.json'
            with open(output, 'w') as f:
                json.dump({
                    "scraped_at": "2026-05-17T08:00:00Z",
                    "url": page.url,
                    "body_text": body
                }, f, indent=2, ensure_ascii=False)
            print("Saved to:", output)

            browser.close()

if __name__ == '__main__':
    main()