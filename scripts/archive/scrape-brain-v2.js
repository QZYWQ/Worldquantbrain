#!/usr/bin/env node
/* Login to BRAIN and scrape unsubmitted alphas - v2 with screenshot */

const { chromium } = require('/Users/zpdedn/.nvm/versions/node/v20.20.1/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt';
const API_BASE = 'https://api.worldquantbrain.com';

function nowIso() { return new Date().toISOString(); }
function writeJson(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8');
}

async function login(page, email, password) {
  console.log('Navigating to login page...');
  await page.goto('https://platform.worldquantbrain.com/sign-in', {
    waitUntil: 'domcontentloaded', timeout: 30000
  });
  await page.waitForTimeout(2000);

  // Fill email
  const emailInput = await page.$('input[type="email"], input[name="email"]');
  if (emailInput) {
    await emailInput.fill(email);
    await page.waitForTimeout(300);
  }

  // Fill password
  const passwordInput = await page.$('input[type="password"]');
  if (passwordInput) {
    await passwordInput.fill(password);
    await page.waitForTimeout(300);

    // Submit
    const submitBtn = await page.$('button[type="submit"]');
    if (submitBtn) await submitBtn.click();
  }

  await page.waitForURL('**/alphas/**', { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(5000);
  console.log('Logged in, URL:', page.url());
}

async function scrapePage(page) {
  // Wait for any loading to complete
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.waitForTimeout(3000);

  // Get full page content
  const content = await page.evaluate(() => {
    return {
      url: window.location.href,
      title: document.title,
      bodyText: document.body.innerText?.substring(0, 8000),
      tables: Array.from(document.querySelectorAll('table')).map(t => ({
        rows: t.querySelectorAll('tr').length,
        headers: Array.from(t.querySelectorAll('th')).map(th => th.textContent.trim()),
        firstRows: Array.from(t.querySelectorAll('tr')).slice(0, 5).map(tr =>
          Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim())
        )
      })),
      divsWithAlpha: Array.from(document.querySelectorAll('div')).filter(d =>
        d.textContent.includes('alpha') && d.textContent.length < 200
      ).slice(0, 10).map(d => d.textContent.trim())
    };
  });

  return content;
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

    console.log('\nNavigating to unsubmitted...');
    await page.goto('https://platform.worldquantbrain.com/alphas/unsubmitted', {
      waitUntil: 'domcontentloaded', timeout: 30000
    });
    await page.waitForTimeout(8000);

    console.log('URL:', page.url());

    // Get page info
    const info = await scrapePage(page);
    console.log('\n=== Page Info ===');
    console.log('Title:', info.title);
    console.log('\nBody text (first 3000 chars):');
    console.log(info.bodyText);

    console.log('\n=== Tables ===');
    console.log(JSON.stringify(info.tables, null, 2));

    // Save screenshot
    const screenshotPath = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/screenshot-unsubmitted.png';
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log('\nScreenshot saved:', screenshotPath);

    // Save data
    const outputFile = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/brain-unsubmitted-v2-' + nowIso().replace(/[:.]/g, '-') + '.json';
    writeJson(outputFile, { scraped_at: nowIso(), ...info });
    console.log('Data saved to:', outputFile);

  } finally {
    await browser.close();
  }
}

main().catch(e => {
  console.error('Fatal:', e.message);
  process.exit(1);
});