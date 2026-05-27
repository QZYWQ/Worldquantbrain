#!/usr/bin/env python3
"""Scrape alpha details by intercepting network requests"""

import json
import re

CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt'

ALPHA_IDS = [
    'akAJeKo2', 'QP2eOklr', 'QP2j0XlG', 'qMPbYbjE', 'RR2XQ89d',
    'wpn1GX71', 'xAPQGKZm', 'vRe9G3bz', 'O0b58J1d', 'vReJOJgv',
    '3qan2ekX', 'xAPQoJen', 'om3zeP8b', 'd5Emz02X', 'RR2Yzr8g',
    'gJRKGPov', 'WjaX632k', '0meQ0j3v', 'LLglqor2'
]

def main():
    from playwright.sync_api import sync_playwright

    creds = json.load(open(CRED_FILE))

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=False)
        context = browser.new_context(viewport={"width": 1440, "height": 1200})
        page = context.new_page()

        # Capture all API responses
        api_responses = []
        def handle_response(response):
            url = response.url
            if 'api' in url.lower() or '/alphas/' in url:
                try:
                    body = response.text()
                    api_responses.append({
                        'url': url,
                        'status': response.status,
                        'body': body[:5000] if body else ''
                    })
                except:
                    pass

        page.on('response', handle_response)

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

        print("Logged in, URL:", page.url)

        # Dismiss cookie
        try:
            page.click('button:has-text("Accept All")', timeout=3000)
            page.wait_for_timeout(1000)
        except:
            pass

        # Try Skip button if present
        try:
            page.click('button:has-text("Skip")', timeout=3000)
            page.wait_for_timeout(2000)
        except:
            pass

        results = []
        for alpha_id in ALPHA_IDS:
            print(f"\n=== Scraping {alpha_id} ===")
            api_responses.clear()

            url = f"https://platform.worldquantbrain.com/alphas/{alpha_id}"
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)

            # Dismiss cookie again
            try:
                page.click('button:has-text("Accept All")', timeout=2000)
                page.wait_for_timeout(500)
            except:
                pass

            print(f"  Current URL: {page.url}")

            # Try to get expression via evaluate
            expression_data = page.evaluate("""() => {
                // Look for any JSON data in the page
                const scripts = Array.from(document.querySelectorAll('script'));
                const alphaData = scripts.map(s => {
                    const text = s.innerText;
                    if (text.includes('alphaId') || text.includes('expression')) {
                        return text.substring(0, 2000);
                    }
                    return null;
                }).filter(Boolean);

                // Look for any element with alpha or expression data
                const dataEl = document.querySelector('[data-alpha]');
                const alphaJson = dataEl ? dataEl.getAttribute('data-alpha') : null;

                // Try to get from Redux store or similar
                const stateEl = document.querySelector('#__NEXT_DATA__');
                const nextData = stateEl ? stateEl.textContent : null;

                return {
                    url: window.location.href,
                    alphaDataScripts: alphaData,
                    alphaJsonAttr: alphaJson ? alphaJson.substring(0, 2000) : null,
                    nextData: nextData ? nextData.substring(0, 2000) : null
                };
            }""")

            print(f"  API responses captured: {len(api_responses)}")
            for r in api_responses[:5]:
                print(f"    {r['status']}: {r['url'][:100]}")
                if r['body']:
                    print(f"    Body: {r['body'][:200]}")

            result = {
                'alphaId': alpha_id,
                'url': page.url,
                'expressionData': expression_data,
                'apiResponses': api_responses[:10]
            }

            # Extract expression from API responses if found
            for r in api_responses:
                if 'expression' in r['body'].lower() or alpha_id.lower() in r['url'].lower():
                    print(f"  Found relevant response: {r['url']}")
                    print(f"  Body: {r['body'][:500]}")

            results.append(result)

        # Save
        output = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/alpha-details-intercept.json'
        with open(output, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n\nSaved to {output}")

if __name__ == '__main__':
    main()