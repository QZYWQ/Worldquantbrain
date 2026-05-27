#!/usr/bin/env node
/* Use Chrome DevTools Protocol HTTP to fetch alpha details - simplified */

const http = require('http');
const net = require('net');
const crypto = require('crypto');
const fs = require('fs');

const ALPHA_IDS = [
  'akAJeKo2', 'QP2eOklr', 'QP2j0XlG', 'qMPbYbjE', 'RR2XQ89d',
  'wpn1GX71', 'vRe9G3bz', 'O0b58J1d', 'LLglqor2', '9qaomYb9'
];

const API_BASE = 'https://api.worldquantbrain.com';

function nowIso() {
  return new Date().toISOString().replace(/[:.]/g, '-');
}

function writeJson(file, data) {
  const dir = require('path').dirname(file);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8');
}

function createWebSocketFrame(data) {
  const buf = Buffer.alloc(2 + Buffer.byteLength(data));
  buf[0] = 0x81;
  buf[1] = Buffer.byteLength(data);
  buf.write(data, 2);
  return buf;
}

function parseWebSocketFrames(buf, callbacks) {
  let offset = 0;
  while (offset < buf.length) {
    const opcode = buf[offset] & 0x0f;
    const payloadLen = buf[offset + 1] & 0x7f;

    if (payloadLen > 125) {
      console.log('Large frame, skipping');
      offset = buf.length;
      continue;
    }

    if (buf.length < offset + 2 + payloadLen) {
      break; // Need more data
    }

    const payload = buf.slice(offset + 2, offset + 2 + payloadLen);
    offset += 2 + payloadLen;

    if (opcode === 0x1) { // Text frame
      callbacks.onMessage(payload.toString());
    } else if (opcode === 0x8) { // Close
      callbacks.onClose();
    }
  }
}

async function main() {
  const CDP_PORT = 9222;

  // Get pages
  const pagesResp = await new Promise((resolve, reject) => {
    http.get(`http://localhost:${CDP_PORT}/json`, (res) => {
      let data = ''; res.on('data', c => data += c); res.on('end', () => resolve(data));
    }).on('error', reject);
  });

  const pages = JSON.parse(pagesResp);
  console.log('Available pages:', pages.length);

  const brainPage = pages.find(p => p.url && p.url.includes('worldquantbrain'));
  if (!brainPage) {
    throw new Error('No BRAIN page found');
  }
  console.log(`Using: ${brainPage.id} - ${brainPage.title}`);

  const wsUrl = brainPage.webSocketDebuggerUrl;
  const wsUrlMatch = wsUrl.match(/ws:\/\/([^:]+):(\d+)(.*)/);
  if (!wsUrlMatch) throw new Error('Invalid WebSocket URL: ' + wsUrl);
  const [, wsHost, wsPortStr, wsPath] = wsUrlMatch;
  const wsPort = parseInt(wsPortStr, 10);

  console.log(`Connecting to WebSocket: ${wsHost}:${wsPort}${wsPath}`);

  // Create TCP connection
  const client = await new Promise((resolve, reject) => {
    const c = net.createConnection({ host: wsHost, port: wsPort }, () => resolve(c));
    c.on('error', reject);
  });

  // WebSocket handshake
  const key = crypto.randomBytes(16).toString('base64');
  const handshake = `GET ${wsPath} HTTP/1.1\r\nHost: ${wsHost}:${wsPort}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: ${key}\r\nSec-WebSocket-Version: 13\r\n\r\n`;
  client.write(handshake);

  let wsConnected = false;
  let response = '';
  let idCounter = 1;
  const pendingRequests = {};

  client.on('data', (data) => {
    if (!wsConnected) {
      response += data.toString();
      if (response.includes('\r\n\r\n')) {
        wsConnected = true;
        console.log('WebSocket connected!');
        processAlphas();
      }
    } else {
      // Handle WebSocket frames
      parseWebSocketFrames(data, {
        onMessage: (msg) => {
          try {
            const parsed = JSON.parse(msg);
            console.log('Received:', JSON.stringify(parsed).substring(0, 100));
            const id = parsed.id;
            if (id && pendingRequests[id]) {
              clearTimeout(pendingRequests[id].timeout);
              pendingRequests[id].resolve(parsed);
              delete pendingRequests[id];
            }
          } catch (_) {}
        },
        onClose: () => {
          console.log('WebSocket closed');
          client.end();
        }
      });
    }
  });

  function sendWsMessage(method, params) {
    return new Promise((resolve, reject) => {
      const id = idCounter++;
      const msg = JSON.stringify({ id, method, params });
      console.log(`Sending: ${method} (id=${id})`);
      const frame = createWebSocketFrame(msg);
      client.write(frame);

      const timeout = setTimeout(() => {
        delete pendingRequests[id];
        reject(new Error('timeout for ' + method));
      }, 30000);

      pendingRequests[id] = { resolve, reject, timeout };
    });
  }

  async function processAlphas() {
    try {
      // First navigate to API
      console.log('\nNavigating to API...');
      await sendWsMessage('Page.navigate', { url: `${API_BASE}/` });
      await new Promise(r => setTimeout(r, 2000));

      const results = [];
      for (const alphaId of ALPHA_IDS) {
        console.log(`\nFetching ${alphaId}...`);

        try {
          const evalResult = await sendWsMessage('Runtime.evaluate', {
            expression: `fetch('/alphas/${alphaId}', {credentials: 'include', headers: {'Accept': 'application/json', 'Content-Type': 'application/json'}}).then(r => r.json())`,
            returnByValue: true,
            awaitPromise: true
          });

          console.log('  Response received');
          const value = evalResult?.result?.value;
          if (!value || value.error) {
            console.log(`  Error: ${value?.error || 'no result'}`);
            results.push({ alphaId, error: value?.error || 'no result' });
            continue;
          }

          const detail = value;
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

      const outputFile = `/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/alpha-details-cdp3-${nowIso()}.json`;
      writeJson(outputFile, {
        captured_at: new Date().toISOString(),
        source: 'chrome_cdp_http',
        alphas: results,
      });
      console.log(`\n\nSaved to: ${outputFile}`);

    } catch (err) {
      console.error('Error:', err.message);
    } finally {
      client.end();
    }
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});