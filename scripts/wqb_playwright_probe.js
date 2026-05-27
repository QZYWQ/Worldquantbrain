#!/usr/bin/env node
/* Run or resume a bounded WorldQuant BRAIN probe batch with Playwright. */

const fs = require('fs');
const path = require('path');
const { chromium } = require('/private/tmp/wqb-pw/node_modules/playwright');

const API_BASE = 'https://api.worldquantbrain.com';
const SOURCE_ROOT = path.join(process.env.HOME, 'Library/Application Support/Google/Chrome');
const PROFILE = process.env.WQB_CHROME_PROFILE || 'Profile 1';
const CACHE_ROOT = '/private/tmp/wqb-playwright-profile';

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function writeJson(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8');
}

function nowIso() {
  return new Date().toISOString();
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

function mergeSettings(candidate) {
  return {
    instrumentType: 'EQUITY',
    region: 'USA',
    universe: 'TOP3000',
    delay: 1,
    decay: 0,
    neutralization: 'INDUSTRY',
    truncation: 0.08,
    pasteurization: 'ON',
    unitHandling: 'VERIFY',
    nanHandling: 'OFF',
    language: 'FASTEXPR',
    visualization: false,
    ...(candidate.settings || {}),
  };
}

function extractSimulationUrl(record) {
  if (record && record.submit_location) return record.submit_location;
  const error = String((record && record.error) || '');
  const match = error.match(/https:\/\/api\.worldquantbrain\.com\/simulations\/[A-Za-z0-9]+/);
  return match ? match[0] : null;
}

function alphaIdFromSimulation(simulation) {
  if (!simulation || typeof simulation !== 'object') return null;
  if (typeof simulation.alpha === 'string') return simulation.alpha;
  if (simulation.alpha && typeof simulation.alpha === 'object') {
    return simulation.alpha.id || simulation.alpha.alpha_id || simulation.alpha.alphaId || null;
  }
  return null;
}

function compactMetrics(alphaDetail) {
  const is = alphaDetail && alphaDetail.is;
  if (!is || typeof is !== 'object') return {};
  return {
    sharpe: is.sharpe,
    fitness: is.fitness,
    turnover: is.turnover,
    returns: is.returns,
    drawdown: is.drawdown,
    margin: is.margin,
    longCount: is.longCount,
    shortCount: is.shortCount,
  };
}

function compactChecks(alphaDetail) {
  const checks = alphaDetail && alphaDetail.is && alphaDetail.is.checks;
  return Array.isArray(checks) ? checks : [];
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

async function submitSimulation(page, expression, settings) {
  const response = await apiFetch(page, `${API_BASE}/simulations`, {
    method: 'POST',
    body: JSON.stringify({ type: 'REGULAR', settings, regular: expression }),
  });
  if (!response.ok) {
    throw new Error(`submit failed status=${response.status} body=${String(response.text || '').slice(0, 300)}`);
  }
  const location = response.headers.location || response.headers.Location;
  if (location) return location;
  const id = response.json && (response.json.id || response.json.simulation_id || response.json.simulationId);
  if (id) return `${API_BASE}/simulations/${id}`;
  throw new Error('submit response missing Location/id');
}

async function pollSimulation(page, location, maxPolls) {
  for (let i = 0; i < maxPolls; i += 1) {
    const response = await apiFetch(page, location);
    if (!response.ok) {
      throw new Error(`poll failed status=${response.status} body=${String(response.text || '').slice(0, 300)}`);
    }
    const retryAfter = Number(response.headers['retry-after'] || 0);
    if (retryAfter > 0) {
      await page.waitForTimeout(retryAfter * 1000);
      continue;
    }
    const payload = response.json;
    if (!payload || typeof payload !== 'object') {
      throw new Error('poll response missing JSON object');
    }
    const status = String(payload.status || '').toUpperCase();
    if (['COMPLETE', 'ERROR', 'WARNING'].includes(status)) return payload;
    await page.waitForTimeout(20000);
  }
  throw new Error(`simulation did not finish after ${maxPolls} polls: ${location}`);
}

async function fetchAlphaDetail(page, alphaId) {
  const response = await apiFetch(page, `${API_BASE}/alphas/${alphaId}`);
  if (!response.ok) {
    throw new Error(`alpha detail failed status=${response.status} body=${String(response.text || '').slice(0, 300)}`);
  }
  if (!response.json || typeof response.json !== 'object') {
    throw new Error(`alpha detail missing JSON object for ${alphaId}`);
  }
  return response.json;
}

function findExisting(existing, name) {
  const alphas = existing && Array.isArray(existing.alphas) ? existing.alphas : [];
  return alphas.find((item) => item && item.name === name) || null;
}

async function main() {
  const input = process.argv[2];
  const output = process.argv[3];
  const existingPath = process.argv[4] || output;
  if (!input || !output) {
    throw new Error('usage: node scripts/wqb_playwright_probe.js <input.json> <output.json> [existing.json]');
  }

  const batch = readJson(input);
  const existing = fs.existsSync(existingPath) ? readJson(existingPath) : {};
  const candidates = batch.candidates || [];

  copyProfile();
  const context = await chromium.launchPersistentContext(CACHE_ROOT, {
    channel: 'chrome',
    headless: false,
    args: [`--profile-directory=${PROFILE}`, '--disable-blink-features=AutomationControlled'],
    viewport: { width: 1440, height: 1200 },
  });
  const page = context.pages()[0] || await context.newPage();

  try {
    await page.goto('https://platform.worldquantbrain.com/simulate', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(5000);
    await page.goto(`${API_BASE}/`, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(2000);

    const records = [];
    for (let i = 0; i < candidates.length; i += 1) {
      const candidate = candidates[i];
      const name = candidate.name || `candidate_${i + 1}`;
      const previous = findExisting(existing, name);

      if (previous && previous.alpha_id && previous.metrics) {
        records.push(previous);
        console.log(`[${i + 1}/${candidates.length}] keep ${name} alpha=${previous.alpha_id}`);
        continue;
      }

      const record = {
        ...(previous || {}),
        name,
        expression: candidate.expression,
        settings: mergeSettings(candidate),
        source: 'playwright_chrome_profile',
        submitted_at: (previous && previous.submitted_at) || nowIso(),
      };

      try {
        let location = extractSimulationUrl(previous);
        if (location) {
          console.log(`[${i + 1}/${candidates.length}] poll existing ${name}`);
        } else {
          console.log(`[${i + 1}/${candidates.length}] submit ${name}`);
          location = await submitSimulation(page, candidate.expression, record.settings);
        }
        record.submit_location = location;
        const simulation = await pollSimulation(page, location, 45);
        record.simulation_result = simulation;
        const alphaId = alphaIdFromSimulation(simulation);
        record.alpha_id = alphaId;
        if (alphaId) {
          const alphaDetail = await fetchAlphaDetail(page, alphaId);
          record.alpha_detail = alphaDetail;
          record.metrics = compactMetrics(alphaDetail);
          record.checks = compactChecks(alphaDetail);
          delete record.error;
        } else {
          record.error = 'simulation completed without alpha id';
        }
      } catch (error) {
        record.error = String(error && error.message ? error.message : error);
      }
      record.completed_at = nowIso();
      records.push(record);
      const metrics = record.metrics || {};
      const fail = Array.isArray(record.checks)
        ? record.checks.filter((check) => check && check.result === 'FAIL').map((check) => check.name)
        : [];
      console.log(
        `  alpha=${record.alpha_id || '-'} sharpe=${metrics.sharpe ?? '-'} fitness=${metrics.fitness ?? '-'} ` +
          `turnover=${metrics.turnover ?? '-'} returns=${metrics.returns ?? '-'} fail=${fail.join(',') || '-'}`
      );
      writeJson(output, {
        capture_id: batch.capture_id || path.basename(output, '.json'),
        topic: batch.topic,
        source: 'official_worldquantbrain_api',
        auth_mode: 'playwright_chrome_profile',
        captured_at: nowIso(),
        candidates_source: input,
        resumed_from: existingPath,
        alphas: records,
      });
    }

    writeJson(output, {
      capture_id: batch.capture_id || path.basename(output, '.json'),
      topic: batch.topic,
      source: 'official_worldquantbrain_api',
      auth_mode: 'playwright_chrome_profile',
      captured_at: nowIso(),
      candidates_source: input,
      resumed_from: existingPath,
      alphas: records,
    });
  } finally {
    await context.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
