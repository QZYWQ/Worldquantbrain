#!/usr/bin/env node
/* Use Playwright with existing Chrome profile to fetch alpha details */

const { chromium } = require('/Users/zpdedn/.nvm/versions/node/v20.20.1/lib/node_modules/playwright');
const path = require('path');
const fs = require('fs');

const CHROME_BASE = path.join(process.env.HOME, 'Library/Application Support/Google/Chrome');
const PROFILE = 'Profile 1';

const ALPHA_IDS = [
  'akAJeKo2', 'QP2eOklr', 'QP2j0XlG', 'qMPbYbjE', 'RR2XQ89d',
  'wpn1GX71', 'vRe9G3bz', 'O0b58J1d', 'LLglqor2', '9qaomYb9'
];

const API_BASE = 'https://api.worldquantbrain.com';

function nowIso() {
  return new Date().toISOString().replace(/[:.]/g, '-');
}

function writeJson(file, data) {
  const dir = path.dirname(file);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8');
}

async function main() {
  console.log('Launching browser with existing profile...');

  const context = await chromium.launchPersistentContext(path.join(CHROME_BASE, PROFILE), {
    channel: 'chrome',
    headless: false,
    viewport: { width: 1440, height: 1200 },
  });

  const page = context.pages()[0] || await context.newPage();

  // Go to BRAIN platform to establish session
  console.log('Navigating to BRAIN platform...');
  await page.goto('https://platform.worldquantbrain.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);

  console.log('Current URL:', page.url());

  const results = [];

  for (const alphaId of ALPHA_IDS) {
    console.log(`\nFetching ${alphaId}...`);

    try {
      // Navigate to the alpha page
      await page.goto(`https://platform.worldquantbrain.com/alphas/${alphaId}`, {
        waitUntil: 'networkidle',
        timeout: 20000
      });
      await page.waitForTimeout(2000);

      const url = page.url();
      console.log(`  URL: ${url}`);

      if (url.includes('/alphas/unsubmitted')) {
        results.push({ alphaId, error: 'redirected to unsubmitted list' });
        continue;
      }

      // Try to get metrics from the page
      const metrics = await page.evaluate(() => {
        const text = document.body.innerText;
        const result = {};

        const sharpeMatch = text.match(/Sharpe[:\s]*([0-9.]+)/i);
        if (sharpeMatch) result.sharpe = parseFloat(sharpeMatch[1]);

        const fitnessMatch = text.match(/Fitness[:\s]*([0-9.]+)/i);
        if (fitnessMatch) result.fitness = parseFloat(fitnessMatch[1]);

        const scMatch = text.match(/Self[Cc]orrelation[:\s]*([0-9.]+)/i);
        if (scMatch) result.selfCorrelation = parseFloat(scMatch[1]);

        const decayMatch = text.match(/Decay[:\s]*([0-9]+)/i);
        if (decayMatch) result.decay = parseInt(decayMatch[1]);

        const neutMatch = text.match(/Neutralization[:\s]*([A-Za-z]+)/i);
        if (neutMatch) result.neutralization = neutMatch[1];

        return result;
      });

      console.log(`  Metrics from page:`, JSON.stringify(metrics));
      results.push({ alphaId, url, pageMetrics: metrics });

    } catch (err) {
      console.log(`  Error: ${err.message}`);
      results.push({ alphaId, error: err.message });
    }
  }

  await context.close();

  const outputFile = `/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/alpha-details-page-${nowIso()}.json`;
  writeJson(outputFile, {
    captured_at: new Date().toISOString(),
    source: 'playwright_profile',
    alphas: results,
  });
  console.log(`\n\nSaved to: ${outputFile}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});