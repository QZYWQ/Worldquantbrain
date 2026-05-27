#!/usr/bin/env node
const fs = require('fs');
const https = require('https');

const CRED_FILE = '/Users/zpdedn/Documents/project/Worldquantbrain/credential.txt';
const creds = JSON.parse(fs.readFileSync(CRED_FILE, 'utf8'));
const [email, password] = creds;

const options = {
  hostname: 'api.worldquantbrain.com',
  path: '/users/self/alphas?status=UNSUBMITTED&ordering=-sharpe&limit=50',
  method: 'GET',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  },
  auth: email + ':' + password
};

console.log('Making API request...');
const req = https.request(options, (res) => {
  console.log('Status:', res.statusCode);
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => {
    console.log('Response (first 10000 chars):');
    console.log(data.substring(0, 10000));
    const outputFile = '/Users/zpdedn/Documents/project/Worldquantbrain/runs/simulation-captures/api-unsub-' + new Date().toISOString().replace(/[:.]/g, '-') + '.json';
    fs.writeFileSync(outputFile, data);
    console.log('\nSaved:', outputFile);
  });
});

req.on('error', (e) => console.error('Error:', e.message));
req.end();