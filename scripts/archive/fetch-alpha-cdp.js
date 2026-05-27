#!/usr/bin/env node
/* Fetch alpha details using Chrome DevTools Protocol (CDP) */

const http = require('http');
const fs = require('fs');
const path = require('path');

const CACHE_ROOT = '/private/tmp/wqb-playwright-profile';
const PROFILE = process.env.WQB_CHROME_PROFILE || 'Profile 1';

const ALPHA_IDS = [
  'akAJeKo2', 'QP2eOklr', 'QP2j0XlG', 'qMPbYbjE', 'RR2XQ89d',
  'wpn1GX71', 'vRe9G3bz', 'O0b58J1d', 'LLglqor2', '9qaomYb9'
];

const API_BASE = 'https://api.worldquantbrain.com';

function nowIso() {
  return new Date().toISOString();
}

function writeJson(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8');
}

function cdpRequest(port, method, params = {}) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({ method, params });
    const options = {
      hostname: 'localhost',
      port,
      path: '/json',
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(postData) }
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(new Error(`CDP parse error: ${data}`)); }
      });
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

function cdpCommand(ws, method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = Date.now() + Math.random();
    const msg = JSON.stringify({ id, method, params });
    let response = null;
    let timeout;

    const onMessage = (data) => {
      try {
        const parsed = JSON.parse(data);
        if (parsed.id === id) {
          clearTimeout(timeout);
          ws.removeListener('message', onMessage);
          resolve(parsed.result);
        }
      } catch (_) {}
    };

    ws.on('message', onMessage);
    timeout = setTimeout(() => {
      ws.removeListener('message', onMessage);
      reject(new Error('CDP command timeout'));
    }, 30000);

    ws.write(msg);
  });
}

async function getCDPWebSocket(port, pageId) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port,
      path: `/json/page/${pageId}`,
      method: 'GET'
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const pages = JSON.parse(data);
          if (pages.length > 0 && pages[0].webSocketDebuggerUrl) {
            resolve(pages[0].webSocketDebuggerUrl);
          } else {
            reject(new Error('No WebSocket URL found'));
          }
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function fetchAlphaDetailCDP(ws, alphaId) {
  // Use fetch through the page context to get alpha details
  const result = await cdpCommand(ws, 'Runtime.evaluate', {
    expression: `
      fetch('${API_BASE}/alphas/${alphaId}', {
        credentials: 'include',
        headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' }
      })
      .then(r => r.json())
      .then(d => JSON.stringify(d))
      .catch(e => JSON.stringify({error: e.message}))
    `,
    returnByValue: true
  });

  if (result && result.result && result.result.value) {
    try {
      return JSON.parse(result.result.value);
    } catch (_) {
      return { raw: result.result.value };
    }
  }
  return { error: 'no result' };
}

async function main() {
  // Get list of pages
  const pagesUrl = `http://localhost:9222/json`;
  const res = await new Promise((resolve, reject) => {
    http.get(pagesUrl, resolve).on('error', reject);
  });

  let data = '';
  res.on('data', chunk => data += chunk);
  const pages = await new Promise((resolve, reject) => {
    res.on('end', () => { try { resolve(JSON.parse(data)); } catch (e) { reject(e); } });
  });

  console.log('Available pages:', pages.length);
  for (const p of pages) {
    console.log(`  ${p.id}: ${p.title} (${p.url})`);
  }

  // Find the BRAIN page
  const brainPage = pages.find(p => p.url && p.url.includes('worldquantbrain.com'));
  if (!brainPage) {
    throw new Error('No BRAIN page found');
  }

  console.log(`\nUsing page: ${brainPage.id} - ${brainPage.title}`);

  // Connect to WebSocket
  const WebSocket = require('ws');
  const wsUrl = brainPage.webSocketDebuggerUrl;
  console.log('Connecting to WebSocket:', wsUrl);

  const ws = new WebSocket(wsUrl);
  await new Promise((resolve, reject) => {
    ws.on('open', resolve);
    ws.on('error', reject);
  });

  console.log('Connected! Fetching alpha details...\n');

  const results = [];
  for (const alphaId of ALPHA_IDS) {
    console.log(`Fetching ${alphaId}...`);
    try {
      const detail = await fetchAlphaDetailCDP(ws, alphaId);

      if (detail.error) {
        console.log(`  Error: ${detail.error}`);
        results.push({ alphaId, error: detail.error });
        continue;
      }

      // Extract relevant fields
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

  ws.close();

  const outputFile = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/alpha-details-cdp-' + nowIso().replace(/[:.]/g, '-') + '.json';
  writeJson(outputFile, {
    captured_at: nowIso(),
    source: 'chrome_cdp',
    alphas: results,
  });
  console.log(`\n\nSaved to: ${outputFile}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});