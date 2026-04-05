import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');

export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 200 },   // Ramp up to 200 users
    { duration: '5m', target: 200 },   // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],
    'errors': ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3333';
const API_KEY = __ENV.API_KEY || 'test-api-key';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json',
};

export default function () {
  // Simulate realistic user behavior
  const actions = [
    () => testHomepage(),
    () => testMCPCatalog(),
    () => testAIGovernance(),
    () => testContactPage(),
    () => testPricing(),
  ];

  // Random action
  const action = actions[Math.floor(Math.random() * actions.length)];
  action();

  // Think time between actions
  sleep(Math.random() * 3 + 1);
}

function testHomepage() {
  const res = http.get(`${BASE_URL}/`);
  check(res, {
    'homepage status 200': (r) => r.status === 200,
    'homepage has title': (r) => r.html('title').text().includes('MEOK'),
  });
  errorRate.add(res.status !== 200);
  responseTime.add(res.timings.duration);
}

function testMCPCatalog() {
  const res = http.get(`${BASE_URL}/mcp/catalog.html`);
  check(res, {
    'catalog status 200': (r) => r.status === 200,
    'catalog has content': (r) => r.body.length > 1000,
  });
  errorRate.add(res.status !== 200);
  responseTime.add(res.timings.duration);
}

function testAIGovernance() {
  const res = http.get(`${BASE_URL}/mcp/ai-governance.html`);
  check(res, {
    'ai-governance status 200': (r) => r.status === 200,
    'ai-governance loads': (r) => r.body.length > 500,
  });
  errorRate.add(res.status !== 200);
  responseTime.add(res.timings.duration);
}

function testContactPage() {
  const res = http.get(`${BASE_URL}/contact.html`);
  check(res, {
    'contact status 200': (r) => r.status === 200,
  });
  errorRate.add(res.status !== 200);
  responseTime.add(res.timings.duration);
}

function testPricing() {
  const res = http.get(`${BASE_URL}/pricing.html`);
  check(res, {
    'pricing status 200': (r) => r.status === 200,
    'pricing has tiers': (r) => r.body.includes('Starter') || r.body.includes('Pro'),
  });
  errorRate.add(res.status !== 200);
  responseTime.add(res.timings.duration);
}

// Spike test
export function spikeTest() {
  const res = http.get(`${BASE_URL}/`);
  errorRate.add(res.status !== 200);
  responseTime.add(res.timings.duration);
}

// Stress test - burst of requests
export function stressTest() {
  const batch = http.batch([
    ['GET', `${BASE_URL}/`],
    ['GET', `${BASE_URL}/mcp/catalog.html`],
    ['GET', `${BASE_URL}/pricing.html`],
  ]);
  
  batch.forEach(res => {
    errorRate.add(res.status !== 200);
    responseTime.add(res.timings.duration);
  });
}
