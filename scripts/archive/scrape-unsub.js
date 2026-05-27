#!/usr/bin/env node
const { chromium } = require('/Users/zpdedn/.nvm/versions/node/v20.20.1/lib/node_modules/playwright');
const https = require('https');
const fs = require('fs');

async function fetchAllAlphas(cookieStr) {
  const alphas = [];
  let offset = 0;
  const limit = 50;

  while (true) {
    const path = `/users/self/alphas?status=UNSUBMITTED&ordering=-sharpe&limit=${limit}&offset=${offset}`;

    const apiOptions = {
      hostname: 'api.worldquantbrain.com',
      path,
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': cookieStr
      }
    };

    const data = await new Promise((resolve, reject) => {
      const req = https.request(apiOptions, (res) => {
        let data = '';
        res.on('data', (chunk) => data += chunk);
        res.on('end', () => resolve({ status: res.statusCode, data }));
      });
      req.on('error', reject);
      req.end();
    });

    if (data.status !== 200) {
      console.log('API returned status', data.status);
      break;
    }

    const json = JSON.parse(data.data);
    if (!json.results || json.results.length === 0) break;

    for (const a of json.results) {
      const selfCorrCheck = a.is && a.is.checks ? a.is.checks.find(c => c.name === 'SELF_CORRELATION') : null;
      alphas.push({
        alphaId: a.id,
        name: a.name || '',
        sharpe: a.is ? a.is.sharpe : null,
        fitness: a.is ? a.is.fitness : null,
        turnover: a.is ? a.is.turnover : null,
        margin: a.is ? a.is.margin : null,
        selfCorr: selfCorrCheck ? selfCorrCheck.value : null,
        status: a.status
      });
    }

    console.log(`Fetched ${alphas.length} alphas (offset ${offset})`);

    if (!json.next) break;
    offset += limit;
  }

  return alphas;
}

async function main() {
  const CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt';
  const creds = JSON.parse(fs.readFileSync(CRED_FILE, 'utf8'));
  const [email, password] = creds;
  const CDP_URL = 'http://127.0.0.1:9222';

  console.log('Connecting to Chrome CDP...');
  const browser = await chromium.connectOverCDP(CDP_URL);
  console.log('Connected!');

  const ctx = browser.contexts()[0];
  let page = ctx.pages()[0];
  if (!page) page = await ctx.newPage();

  // Navigate to sign-in
  console.log('Navigating to sign-in...');
  await page.goto('https://platform.worldquantbrain.com/sign-in', {
    waitUntil: 'domcontentloaded',
    timeout: 30000
  });
  await page.waitForTimeout(3000);

  // Login
  console.log('Filling credentials...');
  await page.locator('input[type="email"]').fill(email);
  await page.waitForTimeout(300);
  await page.locator('input[type="password"]').fill(password);
  await page.waitForTimeout(300);

  console.log('Clicking submit...');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(15000);

  console.log('After login URL:', page.url());

  // Get cookies from the browser session
  const cookies = await ctx.cookies(['https://platform.worldquantbrain.com', 'https://api.worldquantbrain.com']);
  console.log('Got', cookies.length, 'cookies');

  // Build cookie string
  const cookieStr = cookies.map(c => `${c.name}=${c.value}`).join('; ');

  // Fetch all alphas
  console.log('\nFetching all unsubmitted alphas...');
  const alphas = await fetchAllAlphas(cookieStr);

  console.log('\n' + '='.repeat(100));
  console.log('UNSUBMITTED ALPHAS - Total:', alphas.length);
  console.log('='.repeat(100));
  console.log('ID'.padEnd(12) + 'Name'.padEnd(25) + 'Sharpe'.padEnd(8) + 'Fitness'.padEnd(8) + 'TVR'.padEnd(8) + 'SelfCorr');
  console.log('-'.repeat(100));

  for (const a of alphas) {
    console.log(
      (a.alphaId || '-').padEnd(12) +
      (a.name || '-').padEnd(25) +
      String(a.sharpe != null ? a.sharpe.toFixed(2) : '-').padEnd(8) +
      String(a.fitness != null ? a.fitness.toFixed(2) : '-').padEnd(8) +
      String(a.turnover != null ? a.turnover.toFixed(4) : '-').padEnd(8) +
      String(a.selfCorr != null ? a.selfCorr.toFixed(4) : '-')
    );
  }

  // Save
  const outputFile = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/unsubmitted-full-' + new Date().toISOString().replace(/[:.]/g, '-') + '.json';
  fs.writeFileSync(outputFile, JSON.stringify({
    scraped_at: new Date().toISOString(),
    source: 'api_with_browser_cookies',
    total: alphas.length,
    alphas
  }, null, 2));
  console.log('\nSaved:', outputFile);

  await browser.close();
}

main().catch(e => { console.error('Fatal:', e.message); process.exit(1); });