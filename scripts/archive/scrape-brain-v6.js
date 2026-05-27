#!/usr/bin/env node
/* BRAIN scraper v6 - check API directly and get console logs */

const { chromium } = require('/Users/zpdedn/.nvm/versions/node/v20.20.1/lib/node_modules/playwright');
const fs = require('fs');

const CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt';

function nowIso() { return new Date().toISOString(); }
function writeJson(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

async function login(page, email, password) {
  await page.goto('https://platform.worldquantbrain.com/sign-in', {
    waitUntil: 'domcontentloaded', timeout: 30000
  });
  await page.waitForTimeout(2000);

  const emailInput = await page.$('input[type="email"], input[name="email"]');
  if (emailInput) await emailInput.fill(email);
  await page.waitForTimeout(300);

  const passwordInput = await page.$('input[type="password"]');
  if (passwordInput) {
    await passwordInput.fill(password);
    await page.waitForTimeout(300);
    const submitBtn = await page.$('button[type="submit"]');
    if (submitBtn) await submitBtn.click();
  }

  await page.waitForURL('**/alphas/**', { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(3000);
  console.log('Logged in, URL:', page.url());
}

async function acceptCookies(page) {
  const acceptBtn = await page.$('button:has-text("Accept All")');
  if (acceptBtn) { await acceptBtn.click(); await page.waitForTimeout(500); }
}

async function handleWizard(page) {
  const skipBtn = await page.$('button:has-text("Skip")');
  if (skipBtn) { await skipBtn.click(); await page.waitForTimeout(1500); }
  const continueBtn = await page.$('button:has-text("Continue")');
  if (continueBtn) { await continueBtn.click(); await page.waitForTimeout(1500); }
}

async function main() {
  let creds = null;
  try {
    creds = JSON.parse(fs.readFileSync(CRED_FILE, 'utf8'));
  } catch(e) {
    console.error('Failed to load credentials:', e.message);
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1200 } });
  const page = await context.newPage();

  // Capture console messages
  page.on('console', msg => console.log('BROWSER LOG:', msg.type(), msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.message));

  try {
    await login(page, creds[0], creds[1]);
    await acceptCookies(page);
    await handleWizard(page);

    console.log('\nNavigating to unsubmitted...');
    await page.goto('https://platform.worldquantbrain.com/alphas/unsubmitted', {
      waitUntil: 'domcontentloaded', timeout: 30000
    });
    await page.waitForTimeout(8000);
    await handleWizard(page);

    console.log('URL:', page.url());

    // Get page state
    const pageState = await page.evaluate(() => {
      return {
        url: window.location.href,
        title: document.title,
        bodyText: document.body?.innerText?.substring(0, 5000),
        hasTable: !!document.querySelector('table'),
        tableHTML: document.querySelector('table')?.innerHTML?.substring(0, 2000),
        xhrRequests: window.performance?.getEntriesByType('resource')?.filter(r => r.initiatorType === 'xmlhttprequest').map(r => ({ url: r.name, status: r.responseStatus })) || []
      };
    });

    console.log('\n=== Page State ===');
    console.log('URL:', pageState.url);
    console.log('Has table:', pageState.hasTable);
    console.log('Body text:', pageState.bodyText);
    console.log('Table HTML:', pageState.tableHTML?.substring(0, 1000));
    console.log('XHR requests:', JSON.stringify(pageState.xhrRequests.slice(0, 10), null, 2));

    // Try API call directly
    console.log('\n=== Trying API ===');
    const apiResponse = await page.evaluate(async () => {
      try {
        const resp = await fetch('https://api.worldquantbrain.com/alphas?status=UNSUBMITTED&limit=20', {
          credentials: 'include'
        });
        const text = await resp.text();
        return { status: resp.status, ok: resp.ok, text: text.substring(0, 5000) };
      } catch(e) {
        return { error: e.message };
      }
    });
    console.log('API Response:', JSON.stringify(apiResponse, null, 2));

    // Take screenshot
    const screenshotPath = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/screenshot-unsubmitted-v6.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log('\nScreenshot:', screenshotPath);

    // Save
    const outputFile = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/brain-unsubmitted-v6-' + nowIso().replace(/[:.]/g, '-') + '.json';
    writeJson(outputFile, { scraped_at: nowIso(), ...pageState, apiResponse });
    console.log('Saved to:', outputFile);

  } finally {
    await browser.close();
  }
}

main().catch(e => {
  console.error('Fatal:', e.message);
  process.exit(1);
});