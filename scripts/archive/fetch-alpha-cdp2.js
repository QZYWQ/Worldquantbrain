#!/usr/bin/env node
/* Use Chrome CDP to fetch alpha details via existing browser session */

const { chromium } = require('/Users/zpdedn/.nvm/versions/node/v20.20.1/lib/node_modules/playwright');

const ALPHA_IDS = [
  'akAJeKo2', 'QP2eOklr', 'QP2j0XlG', 'qMPbYbjE', 'RR2XQ89d',
  'wpn1GX71', 'vRe9G3bz', 'O0b58J1d', 'LLglqor2', '9qaomYb9'
];

const API_BASE = 'https://api.worldquantbrain.com';

function nowIso() {
  return new Date().toISOString().replace(/[:.]/g, '-');
}

async function main() {
  const fs = require('fs');
  const path = require('path');

  function writeJson(file, data) {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8');
  }

  console.log('Connecting to existing Chrome via CDP on port 9222...');

  // Connect to existing Chrome
  const browser = await chromium.connect('http://localhost:9222');
  const context = browser.contexts()[0] || await browser.newContext();
  const page = context.pages()[0] || await context.newPage();

  console.log('Connected to page:', page.url());

  // First navigate to establish session
  await page.goto(`${API_BASE}/`, { waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(2000);

  const results = [];

  for (const alphaId of ALPHA_IDS) {
    console.log(`\nFetching ${alphaId}...`);

    try {
      // Use fetch in page context
      const response = await page.evaluate(async (alphaId) => {
        const resp = await fetch(`/alphas/${alphaId}`, {
          credentials: 'include',
          headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' }
        });
        const text = await resp.text();
        try {
          return { ok: resp.ok, status: resp.status, json: JSON.parse(text) };
        } catch (_) {
          return { ok: resp.ok, status: resp.status, text };
        }
      }, alphaId);

      if (!response.ok) {
        console.log(`  Error: HTTP ${response.status}`);
        results.push({ alphaId, error: `HTTP ${response.status}` });
        continue;
      }

      const detail = response.json;
      if (!detail || typeof detail !== 'object') {
        console.log(`  Error: Invalid response`);
        results.push({ alphaId, error: 'Invalid response' });
        continue;
      }

      const expression = detail.regular?.expression || detail.expression;
      const settings = detail.settings || {};
      const metrics = detail.is || {};
      const checks = metrics.checks || [];

      console.log(`  Sharpe: ${metrics.sharpe}, Fitness: ${metrics.fitness}`);
      console.log(`  Self-Correlation: ${metrics.selfCorrelation}`);
      console.log(`  Decay: ${settings.decay}, Neutralization: ${settings.neutralization}`);
      console.log(`  Expression: ${expression ? expression.substring(0, 80) + '...' : 'N/A'}`);

      const failChecks = checks.filter(c => c && c.result === 'FAIL').map(c => c.name);
      if (failChecks.length > 0) {
        console.log(`  FAIL checks: ${failChecks.join(', ')}`);
      }

      results.push({
        alphaId,
        expression,
        settings: {
          decay: settings.decay,
          neutralization: settings.neutralization,
          truncation: settings.truncation,
        },
        metrics: {
          sharpe: metrics.sharpe,
          fitness: metrics.fitness,
          turnover: metrics.turnover,
          returns: metrics.returns,
          drawdown: metrics.drawdown,
          selfCorrelation: metrics.selfCorrelation,
        },
        failChecks,
      });
    } catch (err) {
      console.log(`  Error: ${err.message}`);
      results.push({ alphaId, error: err.message });
    }
  }

  await browser.close();

  const outputFile = `/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/alpha-details-cdp2-${nowIso()}.json`;
  writeJson(outputFile, {
    captured_at: new Date().toISOString(),
    source: 'chrome_cdp_existing',
    alphas: results,
  });
  console.log(`\n\nSaved to: ${outputFile}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});