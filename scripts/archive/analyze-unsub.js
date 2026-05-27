const fs = require('fs');
const data = JSON.parse(fs.readFileSync('/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/unsubmitted-full-2026-05-19T15-33-00-802Z.json', 'utf8'));
console.log('Total unsubmitted:', data.alphas.length);

// Filter for potential submission candidates
const candidates = data.alphas.filter(a =>
  a.sharpe != null && a.sharpe >= 1.0 && a.fitness != null && a.fitness >= 1.0
);

console.log('Sharpe >= 1.0 and Fitness >= 1.0:', candidates.length);
console.log('');
console.log('='.repeat(100));
console.log('POTENTIAL SUBMISSION CANDIDATES (Sharpe >= 1.0, Fitness >= 1.0)');
console.log('='.repeat(100));
console.log('ID'.padEnd(12) + 'Name'.padEnd(25) + 'Sharpe'.padEnd(8) + 'Fitness'.padEnd(8) + 'TVR'.padEnd(8) + 'SelfCorr');
console.log('-'.repeat(100));

candidates.slice(0, 100).forEach(a => {
  console.log(
    (a.alphaId || '-').padEnd(12) +
    (a.name || '-').padEnd(25) +
    String(a.sharpe != null ? a.sharpe.toFixed(2) : '-').padEnd(8) +
    String(a.fitness != null ? a.fitness.toFixed(2) : '-').padEnd(8) +
    String(a.turnover != null ? a.turnover.toFixed(4) : '-').padEnd(8) +
    String(a.selfCorr != null ? a.selfCorr.toFixed(4) : '-')
  );
});