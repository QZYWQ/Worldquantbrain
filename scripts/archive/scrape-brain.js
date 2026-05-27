#!/usr/bin/env node
/* Login to BRAIN and scrape unsubmitted alphas */

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

async function apiFetch(page, url, options = {}) {
  return await page.evaluate(async ({ url, options }) => {
    const response = await fetch(url, {
      credentials: 'include',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options,
    });
    const text = await response.text();
    let json = null;
    try { json = text ? JSON.parse(text) : null; } catch (_err) {}
    return { ok: response.ok, status: response.status, text, json };
  }, { url, options });
}

async function login(page, email, password) {
  console.log('Navigating to login page...');
  await page.goto('https://platform.worldquantbrain.com/sign-in', {
    waitUntil: 'domcontentloaded', timeout: 30000
  });
  await page.waitForTimeout(3000);

  console.log('Current URL:', page.url());

  // Find email input
  const emailInput = await page.$('input[type="email"], input[name="email"], [type="text"]');
  if (emailInput) {
    console.log('Found email input, filling...');
    await emailInput.fill(email);
    await page.waitForTimeout(500);
  } else {
    console.log('No email input found, checking page content...');
    const content = await page.evaluate(() => document.body.innerText.substring(0, 2000));
    console.log('Page content:', content);
  }

  // Find password input
  const passwordInput = await page.$('input[type="password"]');
  if (passwordInput) {
    console.log('Found password input, filling...');
    await passwordInput.fill(password);
    await page.waitForTimeout(500);

    // Submit
    const submitBtn = await page.$('button[type="submit"]');
    if (submitBtn) {
      console.log('Clicking submit...');
      await submitBtn.click();
    }
  }

  await page.waitForTimeout(8000);
  console.log('After login URL:', page.url());
}

async function scrapeTable(page) {
  await page.waitForSelector('table', { timeout: 15000 }).catch(() => null);
  await page.waitForTimeout(3000);

  const rows = await page.evaluate(() => {
    const table = document.querySelector('table');
    if (!table) return [];
    return Array.from(table.querySelectorAll('tr')).map(row =>
      Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim())
    );
  });
  return rows;
}

async function fetchAlphaListViaAPI(page) {
  // Try API endpoint directly
  const response = await apiFetch(page, `${API_BASE}/alphas?status=UNSUBMITTED&limit=100`);
  if (response.ok && response.json) {
    console.log('API response keys:', Object.keys(response.json));
    return response.json;
  }
  console.log('API status:', response.status, response.text?.substring(0, 200));
  return null;
}

async function main() {
  let creds = null;
  try {
    creds = JSON.parse(fs.readFileSync(CRED_FILE, 'utf8'));
    console.log('Loaded credentials for:', creds[0]);
  } catch(e) {
    console.error('Failed to load credentials:', e.message);
    process.exit(1);
  }

  const email = creds[0];
  const password = creds[1];

  console.log('Launching browser...');
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1200 }
  });
  const page = await context.newPage();

  try {
    // Login
    await login(page, email, password);

    // Navigate to unsubmitted
    console.log('\nNavigating to unsubmitted alphas...');
    await page.goto('https://platform.worldquantbrain.com/alphas/unsubmitted', {
      waitUntil: 'networkidle', timeout: 30000
    });
    await page.waitForTimeout(5000);

    console.log('Current URL:', page.url());

    // Try API
    console.log('\nTrying API for alpha list...');
    const apiData = await fetchAlphaListViaAPI(page);
    if (apiData) {
      console.log('API data:', JSON.stringify(apiData, null, 2).substring(0, 3000));
    }

    // Scrape table
    console.log('\nScraping table...');
    const rows = await scrapeTable(page);
    console.log('Table rows:', rows.length);
    if (rows.length > 0) {
      console.log('Header:', rows[0]);
      console.log('First data row:', rows[1] || 'none');
    }

    // Save results
    const outputFile = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/brain-unsubmitted-' + nowIso().replace(/[:.]/g, '-') + '.json';
    writeJson(outputFile, {
      scraped_at: nowIso(),
      url: page.url(),
      rows,
      apiData
    });
    console.log('\nSaved to:', outputFile);

  } finally {
    await browser.close();
  }
}

main().catch(e => {
  console.error('Fatal:', e.message);
  process.exit(1);
});