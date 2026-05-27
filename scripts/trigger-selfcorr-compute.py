#!/usr/bin/env python3
"""Trigger self-correlation check computation for blocked alphas"""

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

        alpha_ids = ['1YoX2GxX', 'd5nbrQ5J', 'ZYjARRL3']

        for alpha_id in alpha_ids:
            print(f"\n{'='*60}")
            print(f"Processing {alpha_id}")

            # First, try to navigate to the alpha and see the UI state
            page.goto(f"https://platform.worldquantbrain.com/alphas/{alpha_id}",
                      wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)

            # Check the current state
            current_state = page.evaluate("""() => {
                // Get all relevant info
                const body = document.body.innerText;

                // Find submit button and its state
                const buttons = Array.from(document.querySelectorAll('button'));
                const submitBtn = buttons.find(b =>
                    b.textContent.includes('Submit') ||
                    b.textContent.includes('submit')
                );

                // Find self-correlation status text
                const hasSelfCorrPending = body.includes('SELF_CORRELATION') && body.includes('PENDING');
                const hasSelfCorrFail = body.includes('SELF_CORRELATION') && body.includes('FAIL');
                const hasSelfCorrPass = body.includes('SELF_CORRELATION') && body.includes('PASS');

                // Find any error message
                const hasError = body.includes('error') || body.includes('Error') || body.includes('cannot');

                return {
                    submitButtonExists: !!submitBtn,
                    submitButtonText: submitBtn?.textContent,
                    submitButtonDisabled: submitBtn?.disabled,
                    hasSelfCorrPending,
                    hasSelfCorrFail,
                    hasSelfCorrPass,
                    hasError,
                    bodySnippet: body.substring(0, 2000)
                };
            }""")

            print(f"  Submit button: {current_state['submitButtonExists']}, text={current_state['submitButtonText']}, disabled={current_state['submitButtonDisabled']}")
            print(f"  Self-corr PENDING: {current_state['hasSelfCorrPending']}")
            print(f"  Self-corr FAIL: {current_state['hasSelfCorrFail']}")
            print(f"  Self-corr PASS: {current_state['hasSelfCorrPass']}")
            print(f"  Has error: {current_state['hasError']}")

            # Try to trigger self-correlation computation by clicking any refresh/recheck button
            # First let's look for buttons that might trigger the check
            buttons_info = page.evaluate("""() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                return buttons.map(b => ({
                    text: b.textContent.trim(),
                    className: b.className,
                    disabled: b.disabled
                }));
            }""")

            print(f"\n  All buttons on page:")
            for btn in buttons_info:
                print(f"    - '{btn['text']}' disabled={btn['disabled']}")

            # Try clicking any "Check" or "Refresh" or "Recalculate" button
            check_btn = page.evaluate("""() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                const targetBtn = buttons.find(b => {
                    const text = b.textContent.toLowerCase();
                    return text.includes('check') || text.includes('refresh') ||
                           text.includes('recalc') || text.includes('run') ||
                           text.includes('self');
                });
                if (targetBtn) {
                    targetBtn.click();
                    return targetBtn.textContent;
                }
                return null;
            }""")

            if check_btn:
                print(f"\n  Clicked button: {check_btn}")
                page.wait_for_timeout(3000)
            else:
                print(f"\n  No check/refresh button found")

            # Try API approach - simulate a "view" to trigger computation
            print(f"\n  Trying API trigger...")
            api_result = page.evaluate(f"""async () => {{
                // Try to GET the alpha with a specific header to trigger computation
                const response = await fetch('https://api.worldquantbrain.com/alphas/{alpha_id}', {{
                    credentials: 'include'
                }});
                const data = JSON.parse(await response.text());

                // Check if there is a self-correlation endpoint
                const scResponse = await fetch(`https://api.worldquantbrain.com/alphas/${{data.id}}/self_correlation`, {{
                    credentials: 'include'
                }});
                return {{
                    status: scResponse.status,
                    text: await scResponse.text().then(t => t.substring(0, 500))
                }};
            }}""")

            print(f"  Self-corr API: {api_result}")

        # Take screenshot of the first alpha
        screenshot_path = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/alpha-detail.png'
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\nScreenshot: {screenshot_path}")

        browser.close()

if __name__ == '__main__':
    main()