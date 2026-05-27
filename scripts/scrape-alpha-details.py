#!/usr/bin/env python3
"""Scrape specific alpha details from BRAIN platform"""

import json
import sys

CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt'

ALPHA_IDS = [
    'akAJeKo2', 'QP2eOklr', 'QP2j0XlG', 'qMPbYbjE', 'RR2XQ89d',
    'wpn1GX71', 'xAPQGKZm', 'vRe9G3bz', 'O0b58J1d', 'vReJOJgv',
    '3qan2ekX', 'xAPQoJen', 'om3zeP8b', 'd5Emz02X', 'RR2Yzr8g',
    'gJRKGPov', 'WjaX632k', '0meQ0j3v', 'LLglqor2'
]

def dismiss_cookie_banner(page):
    """Dismiss cookie consent banner if present"""
    try:
        # Try to find and click "Accept All" button
        accept_btn = page.query_selector('button:has-text("Accept All")')
        if accept_btn:
            accept_btn.click()
            page.wait_for_timeout(1000)
            print("  Dismissed cookie banner")
            return True

        # Try other common selectors
        accept_btn = page.query_selector('button[id*="accept"]')
        if accept_btn:
            accept_btn.click()
            page.wait_for_timeout(1000)
            print("  Dismissed cookie banner (id)")
            return True
    except Exception as e:
        print(f"  Cookie banner dismiss error: {e}")
    return False

def get_page_content(page, alpha_id):
    """Get all relevant content from alpha page"""
    url = f"https://platform.worldquantbrain.com/alphas/{alpha_id}"
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)

    # Dismiss cookie banner
    dismiss_cookie_banner(page)

    # Get body text first to understand what's on the page
    body_text = page.evaluate("document.body?.innerText || ''")

    # Check if we got redirected (session issue or alpha doesn't exist)
    current_url = page.url
    if '/sign-in' in current_url:
        return {"error": "redirected to sign-in - session expired", "url": current_url}
    if '/unsubmitted' in current_url and current_url != url:
        return {"error": "alpha not found or session expired", "url": current_url}

    # Get all text content
    details = page.evaluate("""() => {
        const getTextContent = (sel) => {
            const el = document.querySelector(sel);
            return el ? el.innerText.trim() : null;
        };

        // Try multiple selectors for expression
        const selectors = [
            'textarea[name="expression"]',
            'textarea[id*="expression"]',
            '[data-testid="expression"] textarea',
            '.expression textarea',
            'textarea.alpha-expression',
            'pre.expression',
            '[class*="expression"] textarea',
            'textarea'
        ];

        let expression = null;
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el) {
                expression = el.value || el.innerText;
                if (expression && expression.length > 5) break;
            }
        }

        // Try to find inputs with their values
        const allInputs = Array.from(document.querySelectorAll('input, textarea, select')).map(el => {
            return {tag: el.tagName, name: el.name || el.id || '', type: el.type || '', value: el.value || ''};
        });

        // Get all headings and values from any settings panels
        const settingsPanels = Array.from(document.querySelectorAll('[class*="setting"], [class*="config"], [class*="param"]')).map(el => {
            return el.innerText.substring(0, 200);
        });

        // Get JSON data if embedded
        const scripts = Array.from(document.querySelectorAll('script')).map(s => s.innerText).filter(t => t.includes('alphaId'));

        // Get full HTML for expression area
        const expressionAreaHTML = document.querySelector('[class*="expression"]')?.innerHTML || '';
        const formAreaHTML = document.querySelector('form')?.innerHTML || '';

        return {
            url: window.location.href,
            expression: expression,
            allInputs: allInputs,
            bodyText: document.body.innerText.substring(0, 5000),
            settingsPanels: settingsPanels.slice(0, 20),
            scripts: scripts.slice(0, 3),
            expressionAreaHTML: expressionAreaHTML.substring(0, 2000),
            formAreaHTML: formAreaHTML.substring(0, 2000)
        };
    }""")

    return details

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

        print("Logged in, URL:", page.url)

        # Dismiss cookie banner after login
        dismiss_cookie_banner(page)

        # Verify we're logged in by checking cookies
        cookies = context.cookies()
        print(f"Cookies: {len(cookies)}")

        # Go to unsubmitted to verify session is valid
        page.goto("https://platform.worldquantbrain.com/alphas/unsubmitted",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)
        dismiss_cookie_banner(page)
        print("Unsubmitted page URL:", page.url)
        print("Unsubmitted page title:", page.title())

        results = []
        for alpha_id in ALPHA_IDS:
            print(f"\n=== Scraping {alpha_id} ===")
            try:
                details = get_page_content(page, alpha_id)
                results.append({
                    "alphaId": alpha_id,
                    "success": True,
                    "details": details
                })
                print(f"  URL: {details.get('url', 'N/A')}")
                if 'error' in details:
                    print(f"  ERROR: {details.get('error')}")
                else:
                    print(f"  Expression: {(details.get('expression') or 'NOT FOUND')[:150]}...")
                    print(f"  All inputs: {details.get('allInputs', [])}")
                    print(f"  Body text sample: {details.get('bodyText', '')[:200]}...")
            except Exception as e:
                import traceback
                print(f"  ERROR: {e}")
                traceback.print_exc()
                results.append({
                    "alphaId": alpha_id,
                    "success": False,
                    "error": str(e)
                })

        # Save results
        output = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/alpha-details-scrape.json'
        with open(output, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n\nResults saved to {output}")

        # Take screenshot of last page
        try:
            page.screenshot(path='/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/screenshot-last-alpha.png', full_page=True)
        except:
            pass

if __name__ == '__main__':
    main()