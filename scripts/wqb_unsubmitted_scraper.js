#!/usr/bin/env node
/* Scrape unsubmitted alphas from BRAIN with auto-login fallback */

import { chromium } from '/Users/zpdedn/.nvm/versions/node/v20.20.1/lib/node_modules/playwright/index.mjs';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const API_BASE = 'https://api.worldquantbrain.com';
const CACHE_DIR = '/private/tmp/wqb-playwright-login';
const CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt';

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

async function scrapeTable(page) {
  await page.waitForSelector('table tbody tr', { timeout: 20000 }).catch(() => null);
  await page.waitForTimeout(2000);

  const rows = await page.evaluate(() => {
    const table = document.querySelector('table');
    if (!table) return [];
    return Array.from(table.querySelectorAll('tr')).map(row =>
      Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim())
    );
  });

  const alphas = [];
  for (const row of rows) {
    if (row.length < 8 || !row[1]) continue;
    const alphaId = row[1].trim();
    const name = row[2] ? row[2].trim() : '';
    const sharpe = parseFloat(row[3]) || null;
    const fitness = parseFloat(row[4]) || null;
    const turnover = parseFloat(row[5]) || null;
    const margin = parseFloat(row[6]) || null;
    const selfCorrText = row[7] ? row[7].trim() : '';
    const selfCorr = selfCorrText && selfCorrText !== '-' ? parseFloat(selfCorrText) : null;
    if (alphaId && alphaId.match(/[A-Z0-9]/i)) {
      alphas.push({ alphaId, name, sharpe, fitness, turnover, margin, selfCorr });
    }
  }
  return alphas;
}

async function tryLogin(page, email, password) {
  console.log('Attempting auto-login...');
  // Try to find and fill email field
  const emailInput = await page.$('input[type="email"], input[name="email"], input[id="email"]');
  if (emailInput) {
    await emailInput.fill(email);
    await page.waitForTimeout(500);
  }
  const passwordInput = await page.$('input[type="password"], input[name="password"], input[id="password"]');
  if (passwordInput) {
    await passwordInput.fill(password);
    await page.waitForTimeout(500);
    const submitBtn = await page.$('button[type="submit"], button:has-text("Sign in"), button:has-text("Log in"), button:has-text("Login")');
    if (submitBtn) await submitBtn.click();
    await page.waitForTimeout(3000);
  }
}

async function main() {
  const timestamp = nowIso().replace(/[:.]/g, '-');
  const outputDir = path.join(process.env.HOME, 'Documents/project/Worldquantbrain/runs/simulation-captures');
  const outputFile = path.join(outputDir, `unsubmitted-scrape-${timestamp}.json`);

  let creds = null;
  try {
    creds = JSON.parse(fs.readFileSync(CRED_FILE, 'utf8'));
  } catch(e) { /* ignore */ }

  console.log('Launching browser with logged-in profile...');
  let context;
  try {
    context = await chromium.launchPersistentContext(CACHE_DIR, {
      channel: 'chrome',
      headless: false,
      viewport: { width: 1440, height: 1200 },
    });
  } catch(e) {
    console.log('Profile launch failed, trying fresh browser:', e.message);
    context = await chromium.launch({ headless: false });
    context = await context.newContext({ viewport: { width: 1440, height: 1200 } });
  }

  const page = context.pages()[0] || await context.newPage();

  console.log('Opening BRAIN...');
  await page.goto('https://platform.worldquantbrain.com/alphas/unsubmitted', {
    waitUntil: 'domcontentloaded', timeout: 30000
  });
  await page.waitForTimeout(5000);

  // Check if login page
  const url = page.url();
  if (url.includes('login') || url.includes('signin') || url.includes('auth')) {
    console.log('Detected login page, attempting auto-login...');
    if (creds && Array.isArray(creds) && creds.length >= 2) {
      await tryLogin(page, creds[0], creds[1]);
      await page.waitForTimeout(8000);
    } else {
      console.log('No credentials found, giving user 30s to login manually...');
      await page.waitForTimeout(30000);
    }
  } else {
    console.log('Already logged in, page URL:', url);
    await page.waitForTimeout(3000);
  }

  // Check if still on login page
  const currentUrl = page.url();
  if (currentUrl.includes('login') || currentUrl.includes('signin') || currentUrl.includes('auth')) {
    console.log('Still on login page, giving additional 20s...');
    await page.waitForTimeout(20000);
  }

  console.log('Scraping table...');
  const alphas = await scrapeTable(page);

  console.log(`\nFound ${alphas.length} unsubmitted alphas:`);
  console.log('='.repeat(100));
  console.log('ID'.padEnd(14) + 'Name'.padEnd(30) + 'Sharpe'.padEnd(8) + 'Fitness'.padEnd(8) + 'TVR'.padEnd(8) + 'SelfCorr');
  console.log('-'.repeat(100));
  for (const a of alphas.slice(0, 100)) {
    console.log(
      (a.alphaId || '-').padEnd(14) +
      (a.name || '-').padEnd(30) +
      String(a.sharpe ?? '-').padEnd(8) +
      String(a.fitness ?? '-').padEnd(8) +
      String(a.turnover ?? '-').padEnd(8) +
      String(a.selfCorr ?? '-')
    );
  }

  const result = { scraped_at: nowIso(), source: 'unsubmitted_page', alphas };
  writeJson(outputFile, result);
  console.log(`\nSaved: ${outputFile}`);

  await context.close();
  process.exit(0);
}

main().catch(e => {
  console.error('Fatal:', e.message);
  process.exit(1);
});