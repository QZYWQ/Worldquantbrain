#!/usr/bin/env node
/* Login to BRAIN and scrape unsubmitted alphas - v3 with proper wait */

const { chromium } = require('/Users/zpdedn/.nvm/versions/node/v20.20.1/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt';

function nowIso() { return new Date().toISOString(); }
function writeJson(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8');
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

async function handleWizard(page) {
  // Check for wizard/step dialog
  const skipBtn = await page.$('button:has-text("Skip")');
  if (skipBtn) {
    console.log('Found wizard, clicking Skip...');
    await skipBtn.click();
    await page.waitForTimeout(2000);
  }
  const continueBtn = await page.$('button:has-text("Continue")');
  if (continueBtn) {
    console.log('Found Continue button, clicking...');
    await continueBtn.click();
    await page.waitForTimeout(2000);
  }
}

async function acceptCookies(page) {
  const acceptBtn = await page.$('button:has-text("Accept All")');
  if (acceptBtn) {
    console.log('Accepting cookies...');
    await acceptBtn.click();
    await page.waitForTimeout(1000);
  }
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

  try {
    await login(page, creds[0], creds[1]);
    await acceptCookies(page);

    console.log('\nNavigating to unsubmitted...');
    await page.goto('https://platform.worldquantbrain.com/alphas/unsubmitted', {
      waitUntil: 'domcontentloaded', timeout: 30000
    });

    // Handle wizard if present
    await handleWizard(page);

    // Wait for table or main content to load
    console.log('Waiting for content to load...');
    await page.waitForTimeout(10000);

    // Take screenshot
    const screenshotPath = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/screenshot-unsubmitted-v3.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log('Screenshot:', screenshotPath);

    // Check what's on page
    const html = await page.content();
    console.log('\nPage HTML length:', html.length);

    // Try to find table
    const tableExists = await page.$('table');
    console.log('Table found:', !!tableExists);

    // Wait more if still loading
    if (!tableExists) {
      console.log('Waiting more for table...');
      await page.waitForTimeout(10000);
      await page.screenshot({ path: screenshotPath.replace('.png', '-2.png'), fullPage: true });
    }

    // Get table data
    const tableData = await page.evaluate(() => {
      const table = document.querySelector('table');
      if (!table) return { error: 'no table found', bodyText: document.body.innerText?.substring(0, 5000) };
      const rows = Array.from(table.querySelectorAll('tr'));
      return {
        rowCount: rows.length,
        headers: Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim()),
        data: rows.slice(0, 50).map(row =>
          Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim())
        )
      };
    });

    console.log('\nTable data:', JSON.stringify(tableData, null, 2));

    // Save
    const outputFile = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/brain-unsubmitted-v3-' + nowIso().replace(/[:.]/g, '-') + '.json';
    writeJson(outputFile, { scraped_at: nowIso(), url: page.url(), ...tableData });
    console.log('Saved to:', outputFile);

  } finally {
    await browser.close();
  }
}

main().catch(e => {
  console.error('Fatal:', e.message);
  process.exit(1);
});