#!/usr/bin/env python3
"""Diagnose alpha submission block - check API and page state v2"""

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

        # Check alpha status via API - focus on d5nbrQ5J which has ace_tag
        print("\n=== Checking d5nbrQ5J via API ===")

        result = page.evaluate("""async () => {
            try {
                const response = await fetch('https://api.worldquantbrain.com/alphas/d5nbrQ5J', {
                    credentials: 'include'
                });
                const text = await response.text();
                return { status: response.status, text };
            } catch(e) {
                return { error: e.message };
            }
        }""")

        if result.get('text'):
            data = json.loads(result['text'])
            print(f"Status: {data.get('status')}")
            print(f"Tags: {data.get('tags')}")
            print(f"Classifications: {data.get('classifications')}")
            print(f"Grade: {data.get('grade')}")
            print(f"Stage: {data.get('stage')}")

            # Check IS data
            is_data = data.get('is', {})
            if is_data:
                print(f"\nIS Metrics:")
                print(f"  Sharpe: {is_data.get('sharpe')}")
                print(f"  Fitness: {is_data.get('fitness')}")
                print(f"  Turnover: {is_data.get('turnover')}")
                print(f"  Checks: {is_data.get('checks')}")

            # Check the full response to see if there are any blocks
            for key in data.keys():
                if 'block' in key.lower() or 'restrict' in key.lower() or 'submit' in key.lower() or 'ace' in key.lower():
                    print(f"\n*** Found relevant key: {key} = {data[key]} ***")

        # Now try to navigate and check the UI
        print("\n\n=== Navigating to d5nbrQ5J directly ===")
        page.goto("https://platform.worldquantbrain.com/alphas/d5nbrQ5J",
                  wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(8000)

        print(f"URL: {page.url}")

        # Get the full page state
        page_state = page.evaluate("""() => {
            // Check for any error messages or blocks
            const body = document.body.innerText;
            const hasBlock = body.includes('block') || body.includes('restrict') || body.includes('cannot submit') || body.includes('unable');
            const hasAce = body.includes('ace');

            // Find submit button
            const buttons = Array.from(document.querySelectorAll('button'));
            const submitBtn = buttons.find(b => b.textContent.includes('Submit') || b.textContent.includes('submit'));

            return {
                hasBlock,
                hasAce,
                bodySnippet: body.substring(0, 3000),
                submitButtonExists: !!submitBtn,
                submitButtonText: submitBtn?.textContent,
                submitButtonDisabled: submitBtn?.disabled
            };
        }""")

        print(f"\nPage has 'block' text: {page_state['hasBlock']}")
        print(f"Page has 'ace' text: {page_state['hasAce']}")
        print(f"Submit button exists: {page_state['submitButtonExists']}")
        print(f"Submit button text: {page_state['submitButtonText']}")
        print(f"Submit button disabled: {page_state['submitButtonDisabled']}")
        print(f"\nBody snippet:\n{page_state['bodySnippet'][:2000]}")

        # Screenshot
        screenshot_path = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/d5nbrQ5J-page.png'
        page.screenshot(path=screenshot_path, fullPage=True)
        print(f"\nScreenshot: {screenshot_path}")

        # Try to get the specific element state
        element_check = page.evaluate("""() => {
            // Find the submit button specifically
            const allButtons = Array.from(document.querySelectorAll('button'));
            const submitRelated = allButtons.filter(b => {
                const text = b.textContent.toLowerCase();
                return text.includes('submit') || text.includes('ace');
            });

            return {
                submitRelatedButtons: submitRelated.map(b => ({
                    text: b.textContent.trim(),
                    disabled: b.disabled,
                    className: b.className
                }))
            };
        }""")

        print(f"\nSubmit-related buttons: {json.dumps(element_check['submitRelatedButtons'], indent=2)}")

        browser.close()

if __name__ == '__main__':
    main()