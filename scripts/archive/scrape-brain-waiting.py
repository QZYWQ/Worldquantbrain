#!/usr/bin/env python3
"""Scrape BRAIN - wait for actual data loading"""

import json
import time

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

        try:
            page.click('button:has-text("Continue")', timeout=3000)
            page.wait_for_timeout(2000)
        except:
            pass

        # Navigate to unsubmitted
        print("\nNavigating to unsubmitted...")
        page.goto("https://platform.worldquantbrain.com/alphas/unsubmitted",
                  wait_until="domcontentloaded", timeout=30000)

        # Wait for loading to complete - look for "Loading..." to disappear
        print("Waiting for data to load...")
        for i in range(30):
            body_text = page.evaluate("document.body?.innerText || ''")
            if "Loading..." not in body_text:
                print(f"Loading complete after {i*2} seconds")
                break
            print(f"Still loading... ({i*2}s)")
            page.wait_for_timeout(2000)

        # Now check what's on page
        print("\nChecking for data rows...")
        page.wait_for_timeout(5000)

        # Check HTML structure
        html_info = page.evaluate("""() => {
            // Find any table rows with data
            const allRows = document.querySelectorAll('tr');
            const dataRows = Array.from(allRows).filter(r =>
                r.querySelectorAll('td').length > 0 &&
                r.textContent.trim().length > 0 &&
                !r.textContent.includes('Loading')
            );

            // Check for any clickable elements that might load data
            const loadButtons = Array.from(document.querySelectorAll('button, [role="button"]'))
                .filter(b => b.textContent.trim().length > 0)
                .map(b => ({ text: b.textContent.trim(), class: b.className }));

            // Check for any network activity indicators
            const spinners = document.querySelectorAll('[class*="spinner"], [class*="loading"], [class*="Skeleton"]');

            return {
                totalRows: allRows.length,
                dataRowsCount: dataRows.length,
                firstDataRow: dataRows[0]?.textContent?.trim()?.substring(0, 200),
                loadButtons: loadButtons.slice(0, 10),
                spinnerCount: spinners.length,
                bodySnippet: document.body?.innerText?.substring(0, 2000)
            };
        }""")

        print("\nHTML Info:", json.dumps(html_info, indent=2))

        # Try clicking on something to trigger data
        # The table might need user interaction to load
        try:
            print("\nTrying to interact with filter/page controls...")
            page.click('text=Page size', timeout=3000)
            page.wait_for_timeout(2000)
        except:
            pass

        # Check again
        table_data = page.evaluate("""() => {
            const table = document.querySelector('table');
            if (!table) return { found: false };
            const rows = table.querySelectorAll('tr');
            return {
                found: true,
                rows: rows.length,
                headers: Array.from(table.querySelectorAll('th')).map(t => t.textContent.trim()),
                data: Array.from(rows).slice(0, 50).map(tr =>
                    Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim())
                )
            };
        }""")

        print("\nTable data:", json.dumps(table_data, indent=2))

        # Screenshot
        screenshot_path = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/screenshot-waiting.png'
        page.screenshot(path=screenshot_path, full_page=True)
        print("\nScreenshot:", screenshot_path)

        # Save
        output = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/brain-unsubmitted-waiting.json'
        with open(output, 'w') as f:
            json.dump({
                "scraped_at": "2026-05-17T07:00:00Z",
                "url": page.url,
                "html_info": html_info,
                "table_data": table_data
            }, f, indent=2, ensure_ascii=False)
        print("Saved to:", output)

        browser.close()

if __name__ == '__main__':
    main()