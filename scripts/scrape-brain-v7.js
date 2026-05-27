#!/usr/bin/env node
/* BRAIN scraper v7 - proper login and cookie handling */

const { chromium } = require('/Users/zpdedn/.nvm/versions/node/v20.20.1/lib/node_modules/playwright');
const fs = require('fs');

const CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt';

function nowIso() { return new Date().toISOString(); }
function writeJson(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

async function login(page, email, password) {
  console.log('Going to sign-in page...');
  await page.goto('https://platform.worldquantbrain.com/sign-in', {
    waitUntil: 'domcontentloaded', timeout: 30000
  });
  await page.waitForTimeout(2000);

  console.log('Filling credentials...');
  const emailInput = await page.$('input[type="email"], input[name="email"]');
  if (emailInput) {
    await emailInput.fill(email);
    console.log('Email filled');
  } else {
    console.log('No email input found');
  }
  await page.waitForTimeout(500);

  const passwordInput = await page.$('input[type="password"]');
  if (passwordInput) {
    await passwordInput.fill(password);
    console.log('Password filled');
  }
  await page.waitForTimeout(500);

  const submitBtn = await page.$('button[type="submit"]');
  if (submitBtn) {
    console.log('Clicking submit...');
    await submitBtn.click();
  }

  // Wait for navigation away from sign-in
  console.log('Waiting for navigation...');
  try {
    await page.waitForFunction(() => !window.location.href.includes('sign-in'), { timeout: 15000 });
    console.log('Navigation detected');
  } catch(e) {
    console.log('Navigation timeout, current URL:', page.url());
  }

  await page.waitForTimeout(5000);
  console.log('After login URL:', page.url());

  // Check if we're logged in by looking for user menu
  const userMenu = await page.$('text=User menu, text=Notifications');
  console.log('User menu found:', !!userMenu);
}

async function acceptCookies(page) {
  const acceptBtn = await page.$('button:has-text("Accept All")');
  if (acceptBtn) { await acceptBtn.click(); await page.waitForTimeout(500); }
}

async function handleWizard(page) {
  const skipBtn = await page.$('button:has-text("Skip")');
  if (skipBtn) { await skipBtn.click(); await page.waitForTimeout(2000); }
  const continueBtn = await page.$('button:has-text("Continue")');
  if (continueBtn) { await continueBtn.click(); await page.waitForTimeout(2000); }
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
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1200 },
    extraHTTPHeaders: { 'Accept-Language': 'en-US,en;q=0.9' }
  });
  const page = await context.newPage();

  page.on('console', msg => {
    if (msg.type() === 'error') console.log('BROWSER ERROR:', msg.text());
  });

  try {
    await login(page, creds[0], creds[1]);
    await acceptCookies(page);

    console.log('\nNavigating to unsubmitted...');
    await page.goto('https://platform.worldquantbrain.com/alphas/unsubmitted', {
      waitUntil: 'domcontentloaded', timeout: 30000
    });
    await page.waitForTimeout(8000);
    await handleWizard(page);

    console.log('URL:', page.url());

    // Check cookies
    const cookies = await context.cookies();
    console.log('\nCookies:', cookies.map(c => ({ name: c.name, value: c.value?.substring(0, 20) })));

    // Get page content
    const pageState = await page.evaluate(() => {
      return {
        url: window.location.href,
        title: document.title,
        bodyText: document.body?.innerText?.substring(0, 5000),
      };
    });

    console.log('\nPage title:', pageState.title);
    console.log('Body:', pageState.bodyText?.substring(0, 3000));

    // Try API with cookies
    console.log('\n=== Trying API with cookies ===');
    const apiResponse = await page.evaluate(async () => {
      try {
        const resp = await fetch('https://api.worldquantbrain.com/alphas?status=UNSUBMITTED&limit=10', {
          credentials: 'include'
        });
        const text = await resp.text();
        return { status: resp.status, ok: resp.ok, text: text.substring(0, 3000) };
      } catch(e) {
        return { error: e.message };
      }
    });
    console.log('API:', JSON.stringify(apiResponse, null, 2));

    // Take screenshot
    const screenshotPath = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/screenshot-unsubmitted-v7.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log('\nScreenshot:', screenshotPath);

    // Save
    const outputFile = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/brain-unsubmitted-v7-' + nowIso().replace(/[:.]/g, '-') + '.json';
    writeJson(outputFile, { scraped_at: nowIso(), ...pageState, cookies: cookies.length, apiResponse });
    console.log('Saved to:', outputFile);

  } finally {
    await browser.close();
  }
}

main().catch(e => {
  console.error('Fatal:', e.message);
  process.exit(1);
});