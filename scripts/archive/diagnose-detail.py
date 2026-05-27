#!/usr/bin/env python3
"""Diagnose submit block - accept cookies and get full alpha detail"""

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
            page.wait_for_timeout(1000)
        except:
            pass

        # Skip wizard if any
        try:
            page.click('button:has-text("Skip")', timeout=3000)
            page.wait_for_timeout(2000)
        except:
            pass

        # Now navigate to d5nbrQ5J (which has ace_tag)
        print("\n=== Navigating to d5nbrQ5J ===")
        page.goto("https://platform.worldquantbrain.com/alphas/d5nbrQ5J",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(8000)

        print(f"URL: {page.url}")

        # Check page content
        page_state = page.evaluate("""() => {
            const body = document.body.innerText;
            return {
                url: window.location.href,
                bodyLength: body.length,
                hasAceTag: body.includes('ace'),
                hasSubmit: body.includes('Submit'),
                hasPending: body.includes('PENDING'),
                hasPass: body.includes('PASS'),
                hasFail: body.includes('FAIL'),
                bodySnippet: body.substring(0, 3000)
            };
        }""")

        print(f"\nPage URL: {page_state['url']}")
        print(f"Body length: {page_state['bodyLength']}")
        print(f"Has 'ace': {page_state['hasAceTag']}")
        print(f"Has 'Submit': {page_state['hasSubmit']}")
        print(f"Has 'PENDING': {page_state['hasPending']}")
        print(f"Has 'PASS': {page_state['hasPass']}")
        print(f"Has 'FAIL': {page_state['hasFail']}")
        print(f"\nBody snippet:\n{page_state['bodySnippet'][:2000]}")

        # Find all buttons
        buttons = page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button'));
            return btns.map(b => ({
                text: b.textContent.trim(),
                className: b.className,
                disabled: b.disabled
            }));
        }""")

        print(f"\nAll buttons ({len(buttons)}):")
        for btn in buttons:
            if btn['text']:
                print(f"  '{btn['text']}' disabled={btn['disabled']}")

        # Check for any modal or overlay
        overlays = page.evaluate("""() => {
            const modals = document.querySelectorAll('[class*="modal"], [class*="overlay"], [class*="dialog"], [class*="backdrop"]');
            return {
                count: modals.length,
                styles: modals.map(m => ({
                    display: window.getComputedStyle(m).display,
                    visibility: window.getComputedStyle(m).visibility,
                    opacity: window.getComputedStyle(m).opacity
                }))
            };
        }""")

        print(f"\nOverlays/modals: {overlays['count']}")
        for i, style in enumerate(overlays['styles']):
            print(f"  Modal {i}: display={style['display']}, visibility={style['visibility']}, opacity={style['opacity']}")

        # Try to find the IS metrics section
        is_section = page.evaluate("""() => {
            // Look for elements containing IS metrics
            const allText = document.body.innerText;
            const hasSharpe = allText.includes('Sharpe') || allText.includes('sharpe');
            const hasFitness = allText.includes('Fitness') || allText.includes('fitness');
            const hasSelfCorr = allText.includes('Self-Correlation') || allText.includes('SELF_CORRELATION');

            // Find any metric display
            const metrics = Array.from(document.querySelectorAll('[class*="metric"], [class*="score"], [class*="result"]'));
            return {
                hasSharpe,
                hasFitness,
                hasSelfCorr,
                metricCount: metrics.length,
                metricTexts: metrics.slice(0, 10).map(m => m.textContent.substring(0, 100))
            };
        }""")

        print(f"\nIS Metrics section:")
        print(f"  Has Sharpe: {is_section['hasSharpe']}")
        print(f"  Has Fitness: {is_section['hasFitness']}")
        print(f"  Has Self-Correlation: {is_section['hasSelfCorr']}")
        print(f"  Metric elements: {is_section['metricCount']}")
        for t in is_section['metricTexts']:
            print(f"    {t}")

        # Screenshot
        screenshot = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/d5nbrQ5J-detail.png'
        page.screenshot(path=screenshot)
        print(f"\nScreenshot: {screenshot}")

        browser.close()

if __name__ == '__main__':
    main()