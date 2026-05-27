#!/usr/bin/env node
/* Fetch alpha details by scraping web pages directly */

const fs = require('fs');
const path = require('path');
const { chromium } = require('/Users/zpdedn/.nvm/versions/node/v20.20.1/lib/node_modules/playwright');

const CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt';
const PROFILE = process.env.WQB_CHROME_PROFILE || 'Profile 1';
const SOURCE_ROOT = path.join(process.env.HOME, 'Library/Application Support/Google/Chrome');
const CACHE_ROOT = '/private/tmp/wqb-playwright-profile';

const ALPHA_IDS = [
  'akAJeKo2', 'QP2eOklr', 'QP2j0XlG', 'qMPbYbjE', 'RR2XQ89d',
  'wpn1GX71', 'vRe9G3bz', 'O0b58J1d', 'LLglqor2', '9qaomYb9'
];

function nowIso() {
  return new Date().toISOString();
}

function writeJson(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8');
}

function copyProfile() {
  fs.rmSync(CACHE_ROOT, { recursive: true, force: true });
  fs.mkdirSync(CACHE_ROOT, { recursive: true });
  fs.cpSync(path.join(SOURCE_ROOT, 'Local State'), path.join(CACHE_ROOT, 'Local State'));
  fs.cpSync(path.join(SOURCE_ROOT, PROFILE), path.join(CACHE_ROOT, PROFILE), {
    recursive: true,
    force: true,
    errorOnExist: false,
    filter: (src) => {
      const base = path.basename(src);
      return !['SingletonCookie', 'SingletonLock', 'SingletonSocket', 'DevToolsActivePort'].includes(base);
    },
  });
}

async function login(page, email, password) {
  console.log('Navigating to sign-in page...');
  await page.goto('https://platform.worldquantbrain.com/sign-in', {
    waitUntil: 'domcontentloaded', timeout: 30000
  });
  await page.waitForTimeout(3000);

  const url = page.url();
  console.log('Current URL:', url);

  // Fill email
  const emailInput = await page.$('input[type="email"], input[name="email"], [type="text"]');
  if (emailInput) {
    console.log('Found email input, filling...');
    await emailInput.fill(email);
    await page.waitForTimeout(500);
  }

  // Fill password
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

async function scrapeAlphaPage(page, alphaId) {
  console.log(`\nNavigating to alpha page: ${alphaId}`);
  await page.goto(`https://platform.worldquantbrain.com/alphas/${alphaId}`, {
    waitUntil: 'networkidle', timeout: 30000
  });
  await page.waitForTimeout(3000);

  // Get page content for debugging
  const url = page.url();
  console.log(`  URL: ${url}`);

  // Extract expression
  const expression = await page.evaluate(() => {
    // Try to find expression in various places
    const codeEl = document.querySelector('code, .expression, [data-testid="expression"], textarea');
    if (codeEl) return codeEl.textContent.trim();

    // Try JSON data in page
    const scripts = document.querySelectorAll('script');
    for (const script of scripts) {
      const text = script.textContent;
      if (text.includes('"regular"') || text.includes('"expression"')) {
        const match = text.match(/"regular"\s*:\s*\{[^}]*"expression"\s*:\s*"([^"]+)"/);
        if (match) return match[1];
      }
    }
    return null;
  });

  // Extract metrics/settings from page text
  const pageText = await page.evaluate(() => document.body.innerText);

  // Parse self-correlation
  let selfCorr = null;
  const scMatch = pageText.match(/self.?corr?elation[:\s]*([0-9.]+)/i);
  if (scMatch) selfCorr = parseFloat(scMatch[1]);

  // Parse sharpe
  let sharpe = null;
  const sharpeMatch = pageText.match(/sharpe[:\s]*([0-9.]+)/i);
  if (sharpeMatch) sharpe = parseFloat(sharpeMatch[1]);

  // Parse fitness
  let fitness = null;
  const fitnessMatch = pageText.match(/fitness[:\s]*([0-9.]+)/i);
  if (fitnessMatch) fitness = parseFloat(fitnessMatch[1]);

  // Parse decay
  let decay = null;
  const decayMatch = pageText.match(/decay[:\s]*([0-9]+)/i);
  if (decayMatch) decay = parseInt(decayMatch[1]);

  // Parse neutralization
  let neutralization = null;
  const neutMatch = pageText.match(/neutralization[:\s]*([A-Za-z]+)/i);
  if (neutMatch) neutralization = neutMatch[1];

  return {
    alphaId,
    url,
    expression,
    selfCorrelation: selfCorr,
    sharpe,
    fitness,
    decay,
    neutralization,
    pageText: pageText.substring(0, 500),
  };
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

  console.log('Copying Chrome profile...');
  copyProfile();

  console.log('Launching browser...');
  const context = await chromium.launchPersistentContext(CACHE_ROOT, {
    channel: 'chrome',
    headless: false,
    args: [`--profile-directory=${PROFILE}`, '--disable-blink-features=AutomationControlled'],
    viewport: { width: 1440, height: 1200 },
  });
  const page = context.pages()[0] || await context.newPage();

  try {
    await login(page, email, password);

    const results = [];
    for (const alphaId of ALPHA_IDS) {
      const detail = await scrapeAlphaPage(page, alphaId);
      console.log(`  Sharpe: ${detail.sharpe}, Fitness: ${detail.fitness}`);
      console.log(`  Self-Correlation: ${detail.selfCorrelation}`);
      console.log(`  Decay: ${detail.decay}, Neutralization: ${detail.neutralization}`);
      console.log(`  Expression: ${detail.expression ? detail.expression.substring(0, 80) + '...' : 'N/A'}`);
      results.push(detail);
    }

    const outputFile = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/alpha-details-scrape-' + nowIso().replace(/[:.]/g, '-') + '.json';
    writeJson(outputFile, {
      captured_at: nowIso(),
      source: 'playwright_web_scrape',
      alphas: results,
    });
    console.log(`\n\nSaved to: ${outputFile}`);

  } finally {
    await context.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});