#!/usr/bin/env node
/* Fetch alpha details for specified alpha IDs using Chrome profile */

const fs = require('fs');
const path = require('path');
const { chromium } = require('/Users/zpdedn/.nvm/versions/node/v20.20.1/lib/node_modules/playwright');

const API_BASE = 'https://api.worldquantbrain.com';
const CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt';
const SOURCE_ROOT = path.join(process.env.HOME, 'Library/Application Support/Google/Chrome');
const PROFILE = process.env.WQB_CHROME_PROFILE || 'Profile 1';
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

async function apiFetch(page, url, options = {}) {
  return await page.evaluate(
    async ({ url, options }) => {
      const response = await fetch(url, {
        credentials: 'include',
        headers: { Accept: 'application/json', 'Content-Type': 'application/json', ...(options.headers || {}) },
        ...options,
      });
      const text = await response.text();
      let json = null;
      try {
        json = text ? JSON.parse(text) : null;
      } catch (_err) {}
      return {
        ok: response.ok,
        status: response.status,
        headers: Object.fromEntries(response.headers.entries()),
        text,
        json,
      };
    },
    { url, options }
  );
}

async function fetchAlphaDetail(page, alphaId) {
  // Try the web page first to establish session, then API
  await page.goto(`${API_BASE}/alphas/${alphaId}`, { waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(1500);
  const response = await apiFetch(page, `${API_BASE}/alphas/${alphaId}`);
  if (!response.ok) {
    return { error: `status=${response.status}`, text: response.text };
  }
  return response.json;
}

function extractSettings(detail) {
  if (!detail || !detail.settings) return {};
  const s = detail.settings;
  return {
    decay: s.decay,
    neutralization: s.neutralization,
    truncation: s.truncation,
    universe: s.universe,
    region: s.region,
    delay: s.delay,
  };
}

function extractMetrics(detail) {
  if (!detail || !detail.is) return {};
  const is = detail.is;
  return {
    sharpe: is.sharpe,
    fitness: is.fitness,
    turnover: is.turnover,
    returns: is.returns,
    drawdown: is.drawdown,
    margin: is.margin,
    selfCorrelation: is.selfCorrelation,
    longCount: is.longCount,
    shortCount: is.shortCount,
  };
}

function extractExpression(detail) {
  return detail && detail.regular && detail.regular.expression;
}

function extractChecks(detail) {
  const checks = detail && detail.is && detail.is.checks;
  return Array.isArray(checks) ? checks : [];
}

async function main() {
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
    // Navigate to API base to establish session
    await page.goto(`${API_BASE}/`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(2000);

    const results = [];
    for (const alphaId of ALPHA_IDS) {
      console.log(`\nFetching ${alphaId}...`);
      const detail = await fetchAlphaDetail(page, alphaId);

      if (detail.error) {
        console.log(`  Error: ${detail.error}`);
        results.push({ alphaId, error: detail.error });
        continue;
      }

      const expression = extractExpression(detail);
      const settings = extractSettings(detail);
      const metrics = extractMetrics(detail);
      const checks = extractChecks(detail);
      const selfCorr = metrics.selfCorrelation;

      console.log(`  Sharpe: ${metrics.sharpe}, Fitness: ${metrics.fitness}`);
      console.log(`  Self-Correlation: ${selfCorr}`);
      console.log(`  Decay: ${settings.decay}, Neutralization: ${settings.neutralization}`);
      console.log(`  Expression: ${expression ? expression.substring(0, 100) + '...' : 'N/A'}`);

      const failChecks = checks.filter(c => c && c.result === 'FAIL').map(c => c.name);
      if (failChecks.length > 0) {
        console.log(`  FAIL checks: ${failChecks.join(', ')}`);
      }

      results.push({
        alphaId,
        expression,
        settings,
        metrics,
        selfCorrelation: selfCorr,
        failChecks,
        raw: detail,
      });
    }

    const outputFile = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/alpha-details-fetch-' + nowIso().replace(/[:.]/g, '-') + '.json';
    writeJson(outputFile, {
      captured_at: nowIso(),
      source: 'playwright_chrome_profile',
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