const fs = require('fs');
const https = require('https');

const DATA_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/unsubmitted-full-2026-05-20T19-02-51-888Z.json';
const OUTPUT_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/promising-alpha-details-2026-05-21.json';

const TARGET_IDS = [
  'akAJeKo2', 'QP2eOklr', 'QP2j0XlG', 'qMPbYbjE', 'RR2XQ89d',
  'wpn1GX71', 'vRe9G3bz', 'vReJOJgv', 'LLglqor2',
  'd5ElWjvJ', 'leQzGkJ7', '9qaomYb9', 'KPX6Eq8z', 'Vk2213n0',
  'Grn7QXv0', 'KPn2VRG1'
];

function apiRequest(path, cookieStr) {
  return new Promise(function(resolve, reject) {
    var options = {
      hostname: 'api.worldquantbrain.com',
      path: path,
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Cookie': cookieStr
      }
    };
    var req = https.request(options, function(res) {
      var data = '';
      res.on('data', function(chunk) { data += chunk; });
      res.on('end', function() {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(data) });
        } catch (e) {
          resolve({ status: res.statusCode, data: null, error: e.message, raw: data.substring(0, 500) });
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function main() {
  var playwright = require('/Users/zpdedn/.nvm/versions/node/v20.20.1/lib/node_modules/playwright');
  var browser = await playwright.chromium.connectOverCDP('http://127.0.0.1:9222');
  var ctx = browser.contexts()[0];
  var page = ctx.pages()[0];
  var cookies = await ctx.cookies(['https://api.worldquantbrain.com']);
  var cookieStr = cookies.map(function(c) { return c.name + '=' + c.value; }).join('; ');

  // First fetch the list from API to get proper structure
  console.log('Fetching alphas from API...');
  var r = await apiRequest('/users/self/alphas?limit=500&offset=0', cookieStr);

  if (!r.data || !r.data.results) {
    console.log('Failed to get results:', r.error || r.status);
    await browser.close();
    return;
  }

  var allAlphas = r.data.results;
  console.log('Got', allAlphas.length, 'alphas');

  // Find target alphas
  var targetMap = {};
  allAlphas.forEach(function(a) { targetMap[a.id] = a; });

  var results = [];
  for (var i = 0; i < TARGET_IDS.length; i++) {
    var alphaId = TARGET_IDS[i];
    var alpha = targetMap[alphaId];
    if (alpha) {
      var is = alpha.is || {};
      var checks = is.checks || [];
      var selfCorrCheck = checks.find(function(c) { return c.name === 'SELF_CORRELATION'; });

      results.push({
        alphaId: alphaId,
        name: alpha.name || '',
        sharpe: is.sharpe,
        fitness: is.fitness,
        turnover: is.turnover,
        selfCorr: selfCorrCheck ? selfCorrCheck.value : null,
        selfCorrResult: selfCorrCheck ? selfCorrCheck.result : null,
        expression: alpha.regular ? alpha.regular.code : '',
        checks: checks.map(function(c) { return c.name + ':' + c.result; }).join(', ')
      });
    } else {
      results.push({ alphaId: alphaId, error: 'not found' });
    }
  }

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(results, null, 2), 'utf8');
  console.log('Saved to', OUTPUT_FILE);

  console.log('\n=== ALPHA DETAILS ===');
  for (var j = 0; j < results.length; j++) {
    var r2 = results[j];
    var a = r2;
    console.log('\n' + a.alphaId + ':');
    console.log('  Sharpe:', a.sharpe, 'Fitness:', a.fitness, 'Turnover:', a.turnover);
    console.log('  Self-corr:', a.selfCorr, '(' + (a.selfCorrResult || 'N/A') + ')');
    console.log('  Checks:', a.checks);
    console.log('  Expression:', (a.expression || '').substring(0, 150));
  }

  await browser.close();
}

main().catch(function(e) {
  console.error('Fatal:', e.message);
  process.exit(1);
});