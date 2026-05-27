#!/usr/bin/env python3
"""Scrape BRAIN unsubmitted alphas using Python playwright"""

import json
import os

CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt'

def main():
    from playwright.sync_api import sync_playwright

    creds = json.load(open(CRED_FILE))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1440, "height": 1200})
        page = context.new_page()

        # Login
        print("Going to sign-in...")
        page.goto("https://platform.worldquantbrain.com/sign-in",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        # Fill and submit
        page.fill('input[type="email"], input[name="email"]', creds[0])
        page.wait_for_timeout(300)
        page.fill('input[type="password"]', creds[1])
        page.wait_for_timeout(300)
        page.click('button[type="submit"]')
        page.wait_for_timeout(8000)

        print("Logged in, URL:", page.url)

        # Navigate to unsubmitted
        page.goto("https://platform.worldquantbrain.com/alphas/unsubmitted",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(10000)

        print("URL:", page.url)

        # Get all cookies
        cookies = context.cookies()
        print("\nCookies count:", len(cookies))

        # Check for table
        table_info = page.evaluate("""() => {
            const table = document.querySelector('table');
            if (!table) return { found: false };
            return {
                found: true,
                rows: table.querySelectorAll('tr').length,
                headers: Array.from(table.querySelectorAll('th')).map(t => t.textContent.trim()),
                firstRows: Array.from(table.querySelectorAll('tr')).slice(0, 30).map(tr =>
                    Array.from(tr.querySelectorAll('td, th')).map(td => td.textContent.trim())
                )
            };
        }""")

        print("\nTable:", json.dumps(table_info, indent=2))

        # Check body text
        body_text = page.evaluate("document.body?.innerText?.substring(0, 5000)")
        print("\nBody text:", body_text)

        # Take screenshot
        screenshot_path = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/screenshot-unsubmitted-py.png'
        page.screenshot(path=screenshot_path, full_page=True)
        print("\nScreenshot:", screenshot_path)

        # Save
        output = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/brain-unsubmitted-py.json'
        with open(output, 'w') as f:
            json.dump({
                "scraped_at": "2026-05-17T06:00:00Z",
                "url": page.url,
                "cookies_count": len(cookies),
                "table_info": table_info,
                "body_text": body_text
            }, f, indent=2, ensure_ascii=False)
        print("Saved to:", output)

        browser.close()

if __name__ == '__main__':
    main()