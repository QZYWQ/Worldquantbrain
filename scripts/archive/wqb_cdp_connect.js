#!/usr/bin/env node
/* Connect to Chrome via CDP for BRAIN scraping */

const { chromium } = require('/Users/zpdedn/.nvm/versions/node/v20.20.1/lib/node_modules/playwright');

async function main() {
  const CDP_URL = 'http://127.0.0.1:9222';

  console.log('Trying to connect to Chrome CDP at', CDP_URL);
  let browser;
  try {
    browser = await chromium.connectOverCDP(CDP_URL);
  } catch(e) {
    console.error('CDP connection failed:', e.message);
    console.log('\nChrome not running with remote debugging.');
    console.log('Start Chrome with: open -a "Google Chrome" --args --remote-debugging-port=9222');
    process.exit(1);
  }

  const ctx = browser.contexts()[0];
  let page = ctx.pages()[0];
  if (!page) page = await ctx.newPage();

  console.log('Navigating to unsubmitted alphas...');
  await page.goto('https://platform.worldquantbrain.com/alphas/unsubmitted', {
    waitUntil: 'networkidle', timeout: 30000
  });
  await page.waitForTimeout(5000);

  console.log('URL:', page.url());

  // Get page content
  const bodyText = await page.evaluate(() => document.body.innerText);
  console.log('Page text (first 5000 chars):');
  console.log(bodyText.substring(0, 5000));

  // Parse any table data
  const rows = await page.evaluate(() => {
    const table = document.querySelector('table');
    if (!table) return [];
    return Array.from(table.querySelectorAll('tr')).map(row =>
      Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim())
    );
  });

  console.log('\nTable rows found:', rows.length);

  // Save results
  const fs = require('fs');
  const outputFile = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/unsubmitted-scrape-' + new Date().toISOString().replace(/[:.]/g, '-') + '.json';
  fs.writeFileSync(outputFile, JSON.stringify({
    scraped_at: new Date().toISOString(),
    url: page.url(),
    rows
  }, null, 2));
  console.log('Saved to:', outputFile);

  await browser.close();
  process.exit(0);
}

main().catch(e => {
  console.error('Fatal:', e.message);
  process.exit(1);
});